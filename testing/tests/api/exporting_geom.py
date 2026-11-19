'''
unit tests for pymol.exporting geometry formats
'''

import pytest
import io
import math
import re
import struct
import unittest.mock
import zipfile

import pymol
from pymol import cmd, testing

def file_get_contents(filename, mode='r'):
    with open(filename, mode) as handle:
        return handle.read()

# two atoms with anisotropic displacement parameters, which are drawn as
# ellipsoids by the "ellipsoids" representation
v_pdbstr_anisou = (
    'ATOM      1  N   GLU A 114      24.832  -7.270  -5.728  1.00 33.91           N  \n'
    'ANISOU    1  N   GLU A 114     6968   3709   2207   -518    495    146       N  \n'
    'ATOM      2  CA  GLU A 114      25.839  -6.416  -5.102  1.00 33.68           C  \n'
    'ANISOU    2  CA  GLU A 114     6957   3558   2282   -477    534    166       C  \n'
    'END\n')

# an ANISOU tensor which is not positive definite (eigenvalues -3000, 6000 and
# 15000), so that one ellipsoid semi-axis collapses to zero
v_pdbstr_anisou_indefinite = (
    'ATOM      1  N   GLU A 114      24.832  -7.270  -5.728  1.00 33.91           N  \n'
    'ANISOU    1  N   GLU A 114     6000   6000   6000   9000      0      0       N  \n'
    'END\n')

MATERIAL_BINDING = r'rel material:binding = </PyMOLScene/Materials/(\w+)>'

def save_usda():
    with testing.mktemp('.usda') as filename:
        cmd.save(filename)
        return file_get_contents(filename)

def save_usdz_layer():
    '''
    The layer of a saved USDZ package, which keeps analytic prims
    '''
    with testing.mktemp('.usdz') as filename:
        cmd.save(filename)
        with zipfile.ZipFile(filename) as archive:
            return archive.read('scene.usda').decode()

def usda_translations(contents):
    '''
    Centers of all prims which use a translate-only transform
    '''
    return sorted(
        tuple(round(float(value), 3) for value in match.split(','))
        for match in re.findall(
            r'^        float3 xformOp:translate = \(([^)]*)\)', contents,
            re.M))

def usda_matrices(contents):
    '''
    Rows of all "matrix4d xformOp:transform" values
    '''
    pattern = re.compile(
        r'matrix4d xformOp:transform = \('
        r'\s*\(([^)]*)\),\s*\(([^)]*)\),\s*\(([^)]*)\),\s*\(([^)]*)\)')
    return [
        [tuple(float(value) for value in row.split(',')) for row in match]
        for match in pattern.findall(contents)]

def usda_matrix_translations(contents):
    '''
    Translation rows of all prims which use a full matrix transform
    '''
    return sorted(
        tuple(round(value, 3) for value in matrix[3][:3])
        for matrix in usda_matrices(contents))

def matrix_determinant(matrix):
    (a, b, c), (d, e, f), (g, h, i) = (row[:3] for row in matrix[:3])
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)

def matrix_axis_lengths(matrix):
    return [math.sqrt(sum(value * value for value in row[:3]))
            for row in matrix[:3]]

def usda_prim_block(contents, name):
    '''
    Body of the top level prim with the given name
    '''
    match = re.search(
        r'def \w+ "' + re.escape(name) + r'"[^{]*\{(.*?)\n    \}', contents,
        re.DOTALL)
    return match and match.group(1)

def usda_mesh(contents, prefix):
    '''
    Body of the mesh written for tessellated solids ("Solids") or for the
    scene's triangles ("Mesh")
    '''
    name = re.search(r'def Mesh "(' + prefix + r'_\d+)"', contents).group(1)
    return usda_prim_block(contents, name)

def usda_vec3_array(block, declaration):
    match = re.search(
        re.escape(declaration) + r'\s*=\s*\[(.*?)\]', block, re.DOTALL)
    return [tuple(float(value) for value in item.split(','))
            for item in re.findall(r'\(([^)]*)\)', match.group(1))]

def usda_int_array(block, declaration):
    match = re.search(re.escape(declaration) + r'\s*=\s*\[([^\]]*)\]', block)
    return [int(value) for value in match.group(1).split(',')]

def usda_faces(block):
    indices = usda_int_array(block, 'int[] faceVertexIndices')
    faces, start = [], 0
    for count in usda_int_array(block, 'int[] faceVertexCounts'):
        faces.append(indices[start:start + count])
        start += count
    return faces

def usda_vertex_colors(block):
    palette = usda_vec3_array(block, 'color3f[] primvars:displayColor')
    return [palette[i] for i in
            usda_int_array(block, 'int[] primvars:displayColor:indices')]

def usda_materials(contents):
    '''
    Diffuse color and opacity of each material, by name
    '''
    materials = {}
    for name, body in re.findall(
            r'def Material "(\w+)"\s*\{(.*?)\n        \}', contents,
            re.DOTALL):
        color = re.search(r'inputs:diffuseColor = \(([^)]*)\)', body)
        opacity = re.search(r'inputs:opacity = ([\d.e+-]+)', body)
        materials[name] = (
            tuple(float(value) for value in color.group(1).split(',')),
            float(opacity.group(1)) if opacity else 1.0)
    return materials

def usda_face_materials(block):
    '''
    Material of each face, from the mesh binding or from its GeomSubsets
    '''
    count = len(usda_int_array(block, 'int[] faceVertexCounts'))
    subsets = re.findall(
        r'int\[\] indices = \[([^\]]*)\]\s*' + MATERIAL_BINDING, block)

    if not subsets:
        return [re.search(MATERIAL_BINDING, block).group(1)] * count

    names = [None] * count
    for indices, name in subsets:
        for face in map(int, indices.split(',')):
            if names[face] is not None:
                raise AssertionError('face %d is in two subsets' % face)
            names[face] = name
    return names

def ring_center_and_radius(points):
    center = [sum(point[axis] for point in points) / len(points)
              for axis in range(3)]
    radii = [math.dist(point, center) for point in points]
    return center, radii

def load_cone(r1, r2, c2, cap1=1.0, cap2=1.0):
    from pymol import cgo

    cmd.set('geometry_export_mode', 1)
    cmd.load_cgo([
        cgo.CONE, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, r1, r2,
        1.0, 0.0, 0.0, *c2, cap1, cap2,
    ], 'cone')

def load_custom_cylinders(*specs, c2=(1.0, 0.0, 0.0), alpha=None):
    from pymol import cgo

    cmd.set('geometry_export_mode', 1)
    obj = [] if alpha is None else [cgo.ALPHA, alpha]
    for v1, v2, cap1, cap2 in specs:
        obj += [cgo.CUSTOM_CYLINDER, *v1, *v2, 0.5,
                1.0, 0.0, 0.0, *c2, cap1, cap2]

    cmd.load_cgo(obj, 'cylinders')


def testVRML():
    cmd.fragment('gly')
    for rep in ['spheres', 'sticks', 'surface']:
        cmd.show_as(rep)
        with testing.mktemp('.wrl') as filename:
            cmd.save(filename)
            contents = file_get_contents(filename)
            assert contents.startswith('#VRML V2')


def testUSDA():
    cmd.fragment('gly')
    for rep in ['spheres', 'sticks', 'surface']:
        cmd.show_as(rep)
        contents = save_usda()
        assert contents.startswith('#usda 1.0')
        assert 'metersPerUnit = 1e-10' in contents

        # importers like Blender's drop the material of analytic prims
        assert 'def Mesh' in contents
        for schema in ['Sphere', 'Cylinder', 'Capsule', 'Cone']:
            assert 'def ' + schema not in contents


def testUSDEmptyScene():
    # nothing is displayed, so there is no geometry to export
    assert cmd.get_usda() is None

    with testing.mktemp('.usdz') as filename:
        with pytest.raises(pymol.CmdException):
            cmd.save(filename)


def testUSDZLargeCoordinates():
    from pymol import cgo

    cmd.set('geometry_export_mode', 1)
    cmd.load_cgo([cgo.SPHERE, 1234.567, -2345.678, 3456.789, 1.0], 'sphere')
    contents = save_usdz_layer()

    # six significant digits would round this to 1234.57
    assert usda_translations(contents) == [(1234.567, -2345.678, 3456.789)]


def testUSDZ():
    cmd.fragment('gly')

    for rep, schema in [
            ('spheres', 'def Sphere'),
            ('sticks', 'def Cylinder'),
            ('surface', 'def Mesh')]:
        cmd.show_as(rep)

        with testing.mktemp('.usdz') as filename:
            cmd.save(filename)

            with zipfile.ZipFile(filename) as archive:
                assert archive.namelist() == ['scene.usda']
                info = archive.getinfo('scene.usda')
                assert info.compress_type == zipfile.ZIP_STORED
                contents = archive.read('scene.usda').decode()

            with open(filename, 'rb') as handle:
                handle.seek(info.header_offset)
                header = handle.read(30)
            fields = struct.unpack('<IHHHHHIIIHH', header)
            data_offset = info.header_offset + 30 + fields[-2] + fields[-1]
            assert data_offset % 64 == 0

        assert contents.startswith('#usda 1.0')
        assert 'metersPerUnit = 1\n' in contents
        assert schema in contents


def testUSDZFit():
    from pymol import cgo

    cmd.set('geometry_export_mode', 1)
    cmd.load_cgo([cgo.SPHERE, 10.0, 20.0, 30.0, 1.0], 'sphere')
    contents = save_usdz_layer()

    # the 2 A sphere is scaled to 1 m and stands centered on the ground
    root = contents[:contents.index('\n    def ')]

    def vec3(declaration):
        match = re.search(re.escape(declaration) + r' = \(([^)]*)\)', root)
        return [float(value) for value in match.group(1).split(',')]

    for value in vec3('float3 xformOp:scale'):
        assert value == pytest.approx(0.5, abs=5e-4)

    for value, expected in zip(vec3('float3 xformOp:translate'),
                               (-10.0, -19.0, -30.0)):
        assert value == pytest.approx(expected, abs=5e-4)

    assert 'xformOpOrder = ["xformOp:scale", "xformOp:translate"]' in root


def testUSDZPackageAlignment():
    from pymol import exporting

    contents = b'#usda 1.0\n' + b'\0' * 120
    package = exporting._usdz_package('scene.usda', contents)

    with zipfile.ZipFile(io.BytesIO(package)) as archive:
        info = archive.getinfo('scene.usda')
        assert archive.read('scene.usda') == contents

    offset = info.header_offset
    header = struct.unpack('<IHHHHHIIIHH', package[offset:offset + 30])
    data_offset = offset + 30 + header[-2] + header[-1]
    assert data_offset % 64 == 0


def testUSDZPackageTooLarge():
    from pymol import exporting

    # a ZIP64 local header would carry a second extra field and shift the
    # payload off the 64-byte boundary
    with unittest.mock.patch.object(zipfile, 'ZIP64_LIMIT', 16):
        with pytest.raises(pymol.CmdException) as caught:
            exporting._usdz_package('scene.usda', b'x' * 64)

    assert 'too large' in str(caught.value)


def testUSDZFailureKeepsFile():
    cmd.fragment('gly')

    with testing.mktemp('.usdz') as filename:
        with open(filename, 'wb') as handle:
            handle.write(b'previous')

        # the package is built in memory and written like any other
        # format, so a failure must not truncate an existing file
        with unittest.mock.patch.object(
                zipfile.ZipFile, 'writestr', side_effect=OSError('full')):
            with pytest.raises(OSError):
                cmd.save(filename)

        assert file_get_contents(filename, 'rb') == b'previous'


def testUSDAMaterials():
    from pymol import cgo

    cmd.load_cgo([
        cgo.COLOR, 1.0, 0.0, 0.0,
        cgo.SPHERE, 0.0, 0.0, 0.0, 1.0,
        cgo.SPHERE, 3.0, 0.0, 0.0, 1.0,
        cgo.ALPHA, 0.5,
        cgo.COLOR, 0.0, 0.0, 1.0,
        cgo.SPHERE, 6.0, 0.0, 0.0, 1.0,
    ], 'spheres')

    for contents in [save_usda(), save_usdz_layer()]:
        # AR Quick Look ignores primvar readers, so colors come from
        # constant materials, one per distinct color and opacity
        assert 'UsdPrimvarReader' not in contents
        assert sorted(usda_materials(contents).values()) == [((0.0, 0.0, 1.0), 0.5), ((1.0, 0.0, 0.0), 1.0)]

        # renderers treat any material with an opacity as translucent
        assert contents.count('inputs:opacity') == 1


def testUSDAMeshSubsets():
    cmd.fragment('gly')
    cmd.color('red', 'elem C')
    cmd.color('blue', 'not elem C')
    cmd.show_as('surface')

    contents = save_usda()
    block = usda_mesh(contents, 'Mesh')
    assert 'subsetFamily:materialBind:familyType = "partition"' in block

    names = usda_face_materials(block)
    assert None not in names
    assert len(set(names)) > 1

    # each face takes the color of its first corner
    materials = usda_materials(contents)
    colors = usda_vertex_colors(block)
    for face, name in zip(usda_faces(block), names):
        assert materials[name][0] == colors[face[0]]


def testUSDARampedColors():
    cmd.fragment('gly')
    cmd.ramp_new('usdramp', 'gly', [0, 5], ['red', 'blue'])
    cmd.set('surface_color', 'usdramp', 'gly')
    cmd.show_as('surface', 'gly')

    # the ramp object draws its own color bar, which is not ramp colored
    cmd.disable('usdramp')

    colors = usda_vertex_colors(usda_mesh(save_usda(), 'Mesh'))

    # resolved per vertex between the two ramp colors
    assert len(set(colors)) > 1
    for r, g, b in colors:
        assert r + b == pytest.approx(1.0, abs=0.02)
        assert g == 0.0


def testUSDATriangleMeshWinding():
    cmd.fragment('gly')
    cmd.show_as('surface')

    block = usda_mesh(save_usda(), 'Mesh')
    points = usda_vec3_array(block, 'point3f[] points')
    normals = usda_vec3_array(block, 'normal3f[] normals')
    counts = usda_int_array(block, 'int[] faceVertexCounts')
    indices = usda_int_array(block, 'int[] faceVertexIndices')

    assert len(points) == len(normals)
    assert len(points) == 3 * len(counts)
    assert indices == list(range(len(points)))
    assert set(counts) == {3}

    # every face winds counter-clockwise around its authored normals
    for face in range(len(counts)):
        a, b, c = points[3 * face:3 * face + 3]
        edge1 = [b[i] - a[i] for i in range(3)]
        edge2 = [c[i] - a[i] for i in range(3)]
        cross = [
            edge1[1] * edge2[2] - edge1[2] * edge2[1],
            edge1[2] * edge2[0] - edge1[0] * edge2[2],
            edge1[0] * edge2[1] - edge1[1] * edge2[0]]

        if not any(cross):
            continue

        normal = normals[3 * face]
        assert sum(u * v for u, v in zip(cross, normal)) > 0.0


def testUSDATwoColorSolids():
    from pymol import cgo

    cmd.set('geometry_export_mode', 1)
    red, blue = (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)

    for obj in [
            [cgo.CUSTOM_CYLINDER, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 0.5,
             *red, *blue, 1.0, 1.0],
            [cgo.CONE, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 1.0, 0.0,
             *red, *blue, 1.0, 1.0]]:
        cmd.delete('all')
        cmd.load_cgo(obj, 'solid')

        contents = save_usda()
        block = usda_mesh(contents, 'Solids')
        points = usda_vec3_array(block, 'point3f[] points')
        materials = usda_materials(contents)

        # each face takes one material, so the colors meet halfway like
        # PyMOL's half bonds
        seen = set()
        for face, name in zip(usda_faces(block),
                              usda_face_materials(block)):
            color = materials[name][0]
            heights = [points[i][2] for i in face]
            seen.add(color)

            if color == red:
                assert max(heights) <= 2.5 + 1e-4
            else:
                assert color == blue
                assert min(heights) >= 2.5 - 1e-4

        assert seen == {red, blue}


def testUSDAConeFrustum():
    # a truncated cone must keep both radii, not become one cylinder
    load_cone(2.0, 1.0, (1.0, 0.0, 0.0))
    block = usda_mesh(save_usda(), 'Solids')

    points = usda_vec3_array(block, 'point3f[] points')
    normals = usda_vec3_array(block, 'normal3f[] normals')
    counts = usda_int_array(block, 'int[] faceVertexCounts')
    indices = usda_int_array(block, 'int[] faceVertexIndices')

    assert len(indices) == sum(counts)
    assert max(indices) < len(points)

    for normal in normals:
        assert math.dist(normal, (0.0, 0.0, 0.0)) == pytest.approx(1.0, abs=5e-5)

    segments = counts.count(4)
    assert segments > 8

    # both flat caps are triangle fans over the same segment count
    assert counts.count(3) == 2 * segments

    centers = []
    for offset, radius in [(0, 2.0), (segments, 1.0)]:
        center, radii = ring_center_and_radius(
            points[offset:offset + segments])
        centers.append(center)
        for value in radii:
            assert value == pytest.approx(radius, abs=5e-5)

    assert math.dist(*centers) == pytest.approx(5.0, abs=5e-5)


def testUSDAUncapped():
    for load in [
            lambda: load_cone(2.0, 1.0, (1.0, 0.0, 0.0), 0.0, 0.0),
            lambda: load_custom_cylinders(
                ((0.0, 0.0, 0.0), (0.0, 0.0, 5.0), 0.0, 0.0))]:
        cmd.delete('all')
        load()

        # only the lateral surface, no cap fans
        counts = usda_int_array(
            usda_mesh(save_usda(), 'Solids'), 'int[] faceVertexCounts')
        assert counts.count(3) == 0
        assert len(counts) == counts.count(4)


def testUSDAEllipsoidMesh():
    cmd.read_pdbstr(v_pdbstr_anisou, 'm1', zoom=0)
    cmd.show_as('ellipsoids')
    cmd.set('geometry_export_mode', 1)

    block = usda_mesh(save_usda(), 'Solids')
    points = usda_vec3_array(block, 'point3f[] points')
    normals = usda_vec3_array(block, 'normal3f[] normals')
    half = len(points) // 2

    centers = []
    for start in (0, half):
        ellipsoid = points[start:start + half]
        center = [sum(p[i] for p in ellipsoid) / half for i in range(3)]
        centers.append(tuple(round(value, 2) for value in center))

        # unit normals pointing away from the center, which only holds
        # if they transform with the inverse transpose
        for point, normal in zip(ellipsoid, normals[start:start + half]):
            assert math.dist(normal, (0.0, 0.0, 0.0)) == pytest.approx(1.0, abs=5e-4)
            assert sum(
                (p - c) * n for p, c, n in zip(point, center, normal)) > 0

    assert sorted(centers) == sorted(
        tuple(round(float(value), 2) for value in coord)
        for coord in cmd.get_coords('m1'))


def testUSDASolidQuality():
    from pymol import cgo

    # the ray tracer draws these solids analytically, so PyMOL's quality
    # settings may only raise the exported resolution above the floor
    def cone_segments(value):
        cmd.delete('all')
        cmd.set('cone_quality', value)
        load_cone(2.0, 1.0, (1.0, 0.0, 0.0))
        return usda_int_array(usda_mesh(save_usda(), 'Solids'),
                              'int[] faceVertexCounts').count(4)

    assert cone_segments(3) == 24
    assert cone_segments(48) == 48
    assert cone_segments(1000) == 100

    cmd.delete('all')
    cmd.set('stick_quality', 40)
    load_custom_cylinders(((0.0, 0.0, 0.0), (0.0, 0.0, 5.0), 0.0, 0.0))
    counts = usda_int_array(
        usda_mesh(save_usda(), 'Solids'), 'int[] faceVertexCounts')
    assert counts.count(4) == 40

    # spheres are the bulk of a scene, so they follow sphere_quality
    cmd.delete('all')
    cmd.load_cgo([cgo.SPHERE, 0.0, 0.0, 0.0, 1.0], 'sphere')
    counts = usda_int_array(
        usda_mesh(save_usda(), 'Solids'), 'int[] faceVertexCounts')
    assert counts.count(3) == 2 * 16


@pytest.mark.parametrize("geometry_export_mode", [0, 1])
def testUSDZEllipsoid(geometry_export_mode):
    cmd.read_pdbstr(v_pdbstr_anisou, 'm1', zoom=0)
    cmd.show_as('spheres')
    cmd.show('ellipsoids')
    cmd.turn('x', 35)
    cmd.turn('y', 50)
    cmd.set('geometry_export_mode', geometry_export_mode)

    contents = save_usdz_layer()

    # every ellipsoid is centered on the atom which also carries a sphere,
    # so both must be written in the same coordinate space
    ellipsoids = usda_matrix_translations(contents)
    assert len(ellipsoids) == 2
    assert usda_translations(contents) == ellipsoids

    model = sorted(
        tuple(round(float(value), 3) for value in coord)
        for coord in cmd.get_coords('m1'))

    if geometry_export_mode:
        assert ellipsoids == model
    else:
        assert ellipsoids != model

    for matrix in usda_matrices(contents):
        assertRightHanded(matrix)


def assertRightHanded(matrix):
    # renderers derive inward-pointing normals from a negative determinant
    lengths = matrix_axis_lengths(matrix)
    assert matrix_determinant(matrix) == pytest.approx(lengths[0] * lengths[1] * lengths[2], abs=5e-5)


def testUSDZEllipsoidMirrored():
    cmd.read_pdbstr(v_pdbstr_anisou, 'm1', zoom=0)
    cmd.show_as('ellipsoids')

    # a reflection turns the ellipsoid axes into a left-handed basis
    cmd.transform_object('m1', [
        -1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0])

    matrices = usda_matrices(save_usdz_layer())
    assert len(matrices) == 2

    for matrix in matrices:
        assertRightHanded(matrix)


def testUSDZEllipsoidSheared():
    cmd.read_pdbstr(v_pdbstr_anisou, 'm1', zoom=0)
    cmd.show_as('ellipsoids')

    # a near singular object matrix leaves the ellipsoid axes almost
    # coplanar, which is ill conditioned without being exactly singular
    cmd.transform_object('m1', [
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1e-7, 0.0,
        0.0, 0.0, 0.0, 1.0])

    matrices = usda_matrices(save_usdz_layer())
    assert len(matrices) == 2

    for matrix in matrices:
        for length in matrix_axis_lengths(matrix):
            assert length > 0.0
        # an orthogonal determinant proves the fallback frame was used
        assertRightHanded(matrix)


def testUSDZEllipsoidScale():
    cmd.read_pdbstr(v_pdbstr_anisou, 'm1', zoom=0)
    cmd.show_as('ellipsoids')

    lengths = {}

    for scale in (1.0, 2.0):
        cmd.set('ellipsoid_scale', scale)
        matrices = usda_matrices(save_usdz_layer())
        assert len(matrices) == 2
        lengths[scale] = [
            sorted(matrix_axis_lengths(matrix)) for matrix in matrices]

    # semi-axes carry the ellipsoid size, they are not unit length
    for single, double in zip(lengths[1.0], lengths[2.0]):
        assert single[0] > 0.0
        for one, two in zip(single, double):
            assert two == pytest.approx(one * 2.0, abs=5e-4)


def testUSDZEllipsoidDegenerate():
    cmd.read_pdbstr(v_pdbstr_anisou_indefinite, 'm1', zoom=0)
    cmd.show_as('ellipsoids')

    matrices = usda_matrices(save_usdz_layer())
    assert len(matrices) == 1

    for matrix in matrices:
        # a collapsed semi-axis must not make the transform singular
        lengths = matrix_axis_lengths(matrix)
        for length in lengths:
            assert math.isfinite(length)
            assert length > 0.0
        assertRightHanded(matrix)

        # the collapsed axis stays visually negligible
        assert min(lengths) / max(lengths) == pytest.approx(1e-3, abs=5e-6)


def testUSDZEllipsoidZeroScale():
    cmd.read_pdbstr(v_pdbstr_anisou, 'm1', zoom=0)
    cmd.show_as('ellipsoids')
    cmd.set('ellipsoid_scale', 0)

    # ellipsoids without any extent are omitted rather than exported with
    # an all-zero (singular) transform
    assert 'matrix4d' not in save_usdz_layer()
    assert 'def Mesh' not in save_usda()


def testUSDZAnalyticSolids():
    from pymol import cgo

    cmd.load_cgo([
        cgo.CONE, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 1.0, 0.0,
        1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0,
        cgo.CYLINDER, 4.0, 0.0, 0.0, 4.0, 0.0, 5.0, 1.0,
        0.0, 1.0, 0.0, 0.0, 1.0, 0.0,
        cgo.SAUSAGE, 8.0, 0.0, 0.0, 8.0, 0.0, 5.0, 1.0,
        0.0, 0.0, 1.0, 0.0, 0.0, 1.0,
    ], 'solids')

    # cones, cylinders and capsules share one writer, so schema and prim
    # name must stay in sync
    solids = re.findall(
        r'def (Cone|Cylinder|Capsule) "(\w+)_\d+"', save_usdz_layer())
    assert sorted(schema for schema, _ in solids) == ['Capsule', 'Cone', 'Cylinder']

    for schema, name in solids:
        assert schema == name


def testUSDZSausageIsCapsule():
    from pymol import cgo

    cmd.set('geometry_export_mode', 1)
    cmd.load_cgo([
        cgo.SAUSAGE, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 1.5,
        1.0, 0.0, 0.0, 1.0, 0.0, 0.0,
    ], 'sausage')

    contents = save_usdz_layer()

    # one closed surface rather than a cylinder plus two spheres whose
    # buried hemispheres would darken the solid under transparency
    assert 'def Sphere' not in contents
    assert 'def Cylinder' not in contents

    block = usda_prim_block(contents, 'Capsule_0')
    assert block is not None

    # a capsule's height is its cylindrical spine, the hemispheres reach
    # one radius further along the axis
    assert 'double height = 5' in block
    assert 'double radius = 1.5' in block
    assert usda_vec3_array(block, 'float3[] extent') == [(-1.5, -1.5, -4.0), (1.5, 1.5, 4.0)]
    assert usda_translations(contents) == [(0.0, 0.0, 2.5)]


def testUSDZSticksStayAnalytic():
    # half bonds meet with an uncapped joint, which must not turn the
    # most common representation into meshes
    cmd.fragment('gly')
    cmd.show_as('sticks')

    contents = save_usdz_layer()
    assert 'def Cylinder' in contents
    assert 'def Mesh' not in contents


def testUSDZCustomCylinderJoint():
    # PyMOL leaves the joint between two abutting cylinders uncapped, and
    # the neighbour seals it, so both keep the compact analytic prim
    load_custom_cylinders(
        ((0.0, 0.0, 0.0), (0.0, 0.0, 2.5), 1.0, 0.0),
        ((0.0, 0.0, 2.5), (0.0, 0.0, 5.0), 0.0, 1.0))

    contents = save_usdz_layer()
    assert contents.count('def Cylinder') == 2
    assert 'def Mesh' not in contents


def testUSDZConePointed():
    # UsdGeomCone is always closed at its base, so a cone which PyMOL
    # draws open cannot use it even though it is pointed and one colored
    load_cone(1.0, 0.0, (1.0, 0.0, 0.0), cap1=1.0)
    assert 'def Cone "Cone_0"' in save_usdz_layer()

    cmd.delete('all')
    load_cone(1.0, 0.0, (1.0, 0.0, 0.0), cap1=0.0)
    contents = save_usdz_layer()
    assert 'def Cone' not in contents

    # the base center vertex only exists to fan out the cap
    points = usda_vec3_array(
        usda_mesh(contents, 'Solids'), 'point3f[] points')
    assert (0.0, 0.0, 0.0) not in points


def testUSDZTransparentJointStaysOpen():
    # a closed analytic prim buries an end disc in the joint, which a
    # transparent solid would show as a seam the ray tracer does not draw
    load_custom_cylinders(
        ((0.0, 0.0, 0.0), (0.0, 0.0, 2.5), 1.0, 0.0),
        ((0.0, 0.0, 2.5), (0.0, 0.0, 5.0), 0.0, 1.0),
        alpha=0.5)

    contents = save_usdz_layer()
    assert 'def Cylinder' not in contents

    # the flat outer ends are capped, the joint ends stay open
    block = usda_mesh(contents, 'Solids')
    counts = usda_int_array(block, 'int[] faceVertexCounts')
    assert counts.count(3) == counts.count(4)
    assert 'float[] primvars:displayOpacity = [0.5]' in block


def testUSDZOpaqueRoundCapStaysSphere():
    # while the solid is opaque the buried hemisphere costs nothing to
    # look at, so the compact analytic prims are kept
    load_custom_cylinders(((0.0, 0.0, 0.0), (0.0, 0.0, 5.0), 2.0, 1.0))

    contents = save_usdz_layer()
    assert 'def Cylinder "Cylinder_0"' in contents
    assert contents.count('def Sphere') == 1
    assert 'def Mesh' not in contents


def testUSDZTransparentRoundCapIsDome():
    # a whole cap sphere buries a hemisphere in the barrel, which a
    # transparent solid shows as a darker cap the ray tracer never draws
    load_custom_cylinders(
        ((0.0, 0.0, 0.0), (0.0, 0.0, 5.0), 2.0, 1.0), alpha=0.5)

    contents = save_usdz_layer()
    assert 'def Cylinder' not in contents
    assert 'def Sphere' not in contents

    block = usda_mesh(contents, 'Solids')
    assert 'float[] primvars:displayOpacity = [0.5]' in block

    points = usda_vec3_array(block, 'point3f[] points')
    normals = usda_vec3_array(block, 'normal3f[] normals')
    equator = []

    for point, normal in zip(points, normals):
        if abs(point[2]) < 1e-4:
            equator.append(tuple(round(value, 4) for value in point))
        elif point[2] < 0:
            # on the cap sphere, with unit normals pointing away from
            # the barrel
            assert math.dist(point, (0.0, 0.0, 0.0)) == pytest.approx(0.5, abs=5e-5)
            assert sum(p * n for p, n in zip(point, normal)) == pytest.approx(0.5, abs=5e-5)

    # the dome shares the barrel's open ring, so the two leave no crack
    assert len(equator) == 2 * len(set(equator))


def testUSDZTransparentSausageDomes():
    from pymol import cgo

    cmd.set('geometry_export_mode', 1)
    cmd.load_cgo([
        cgo.ALPHA, 0.5,
        cgo.SAUSAGE, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 1.0,
        1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
    ], 'sausage')

    contents = save_usdz_layer()

    # two colors rule out the capsule, so both caps become open domes
    assert 'def Sphere' not in contents
    assert 'def Capsule' not in contents

    block = usda_mesh(contents, 'Solids')
    points = usda_vec3_array(block, 'point3f[] points')

    # each dome sits beyond its own end, in the color of that end
    for point, color in zip(points, usda_vertex_colors(block)):
        if point[2] < -1e-4:
            assert color == (1.0, 0.0, 0.0)
        elif point[2] > 5.0 + 1e-4:
            assert color == (0.0, 0.0, 1.0)


def testSTL():
    cmd.fragment('gly')
    for rep in ['spheres', 'sticks', 'surface']:
        cmd.show_as(rep)
        with testing.mktemp('.stl') as filename:
            cmd.save(filename)
            contents = file_get_contents(filename, 'rb')
            # 80 bytes header
            # 4 bytes (uint32) number of triangles
            assert len(contents) > 84
            # 50 bytes per triangle
            ntri = int.from_bytes(contents[80:84], 'little')
            assert ntri == (len(contents) - 84) // 50
            assert (len(contents) - 84) % 50 == 0

    cmd.delete('*')
    with testing.mktemp('.stl') as filename:
        with pytest.raises(pymol.CmdException):
            cmd.save(filename)
