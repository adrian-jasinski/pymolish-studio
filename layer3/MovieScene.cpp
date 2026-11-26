/*
 * PyMOL Scene C++ implementation
 *
 * Author: Thomas Holder
 * (c) 2014 Schrodinger, Inc.
 */

#include "os_python.h"
#include "PyMOLGlobals.h"
#include "Util2.h"
#include "Movie.h"
#include "P.h"
#include "PConv.h"
#include "PConvArgs.h"
#include "Setting.h"
#include "View.h"
#include "Selector.h"
#include "Executive.h"
#include "Err.h"
#include "SpecRec.h"
#include "AtomIterators.h"
#include "Feedback.h"
#include "Color.h"
#include "ObjectMolecule.h"

#include <algorithm>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>

#include "MovieScene.h"

/**
 * Get read-only pointer to G->scenes->order
 */
const std::vector<std::string> & MovieSceneGetOrder(PyMOLGlobals * G) {
  return G->scenes->order;
}

/**
 * Get thumbnail of a scene based on name
 */
png_outbuf_t MovieSceneGetThumbnail(PyMOLGlobals* G, pymol::zstring_view name)
{
  auto scenes = G->scenes + cMovieSceneStackDefault;
  auto it = scenes->dict.find(name.c_str());

  if (it == scenes->dict.end()) {
    return {};
  }

  png_outbuf_t out_buf = it->second.thumbnail.getVecData();

  return out_buf;
}

/**
 * Get a unique scene key
 */
std::string CMovieScenes::getUniqueKey()
{
  char key[16];

  for (;; ++scene_counter) {
    snprintf(key, std::size(key), "%03d", scene_counter);

    if (dict.find(key) == dict.end())
      return key;
  }
}

/**
 * Change the ordering of scenes
 *
 * Examples:
 * a b c d e
 * move d behind b with:    order("b d", "current")
 * a b d c e
 * move c to the top with:  order("c", "top")
 * c a b d e
 *
 * @param names space separated list of names to (optionally) sort and to move to
 *        given location
 * @param location current|top|botton
 */
pymol::Result<> MovieSceneOrder(PyMOLGlobals * G, const char * names, bool sort,
    const char * location)
{
  return MovieSceneOrder(G, strsplit(names), sort, location);
}

pymol::Result<> MovieSceneOrder(PyMOLGlobals* G, std::vector<std::string> names_list,
    bool sort, const char* location)
{
  std::vector<std::string> new_order;
  bool is_all = false;

  if (names_list.size() == 1 && names_list[0] == "*") {
    is_all = true;
    names_list = G->scenes->order;
  } else {
    // check that all given names are existing scenes
    for (auto& name : names_list) {
      if (G->scenes->dict.find(name) == G->scenes->dict.end()) {
        return pymol::make_error("Scene '", name, "' is not defined.");
      }
    }
  }

  if (names_list.empty()) {
    return {};
  }

  if (sort) {
    std::sort(names_list.begin(), names_list.end(), strlessnat);
  }

  if (is_all) {
    new_order = std::move(names_list);
  } else {
    std::set<std::string> names_set(names_list.begin(), names_list.end());

    // sanity check: unique keys?
    if (names_set.size() != names_list.size()) {
      return pymol::make_error("Duplicated keys.");
    }

    char loc = location ? location[0] : 'c';

    // sanity check: valid location identifier?
    if (loc != 't' && loc != 'c' && loc != 'b') {
      return pymol::make_error("Invalid location '", location, "'");
    }

    if (loc == 't' /* top */) {
      new_order.insert(new_order.end(), names_list.begin(), names_list.end());
    }

    for (auto& name : G->scenes->order) {
      if (!names_set.count(name)) {
        new_order.push_back(name);
      } else if (loc == 'c' /* current */ && name == names_list[0]) {
        new_order.insert(new_order.end(), names_list.begin(), names_list.end());
      }
    }

    if (loc == 'b' /* bottom */) {
      new_order.insert(new_order.end(), names_list.begin(), names_list.end());
    }
  }

  G->scenes->order = std::move(new_order);

  return {};
}

/*
 * Scene style: the appearance beyond visibility and atom colors
 */

// The settings a scene keeps at the global and at the object level: what
// the presets, looks, themes and "stage" write (modules/pymol/preset.py and
// stage.py; testing/tests/api/scene_style.py checks that none is missing),
// and the size and color settings of the representations. Settings of atoms
// and bonds are kept whichever they are.
static const int cSceneSettings[] = {
    // looks: light and outline
    cSetting_depth_cue, cSetting_ray_trace_mode, cSetting_antialias,
    cSetting_ambient, cSetting_direct, cSetting_reflect, cSetting_shininess,
    cSetting_power, cSetting_light_count, cSetting_spec_count,
    cSetting_specular, cSetting_specular_intensity, cSetting_spec_reflect,
    cSetting_spec_power, cSetting_spec_direct, cSetting_ray_shadow,
    cSetting_ray_shadow_decay_factor, cSetting_ray_shadow_decay_range,
    cSetting_ray_trace_trans_cutoff, cSetting_ray_trace_gain,
    cSetting_ray_trace_color, cSetting_light, cSetting_light2, cSetting_light3,
    cSetting_light4, cSetting_light5, cSetting_light6, cSetting_light7,
    cSetting_light8, cSetting_light9, cSetting_two_sided_lighting,
    cSetting_ambient_occlusion_mode, cSetting_ambient_occlusion_scale,
    // themes and stage: background and fog
    cSetting_bg_rgb, cSetting_bg_rgb_top, cSetting_bg_rgb_bottom,
    cSetting_bg_gradient, cSetting_fog, cSetting_fog_start,
    cSetting_ray_trace_fog, cSetting_cgo_transparency,
    // presets: the shape and color of the representations
    cSetting_cartoon_fancy_helices, cSetting_cartoon_flat_sheets,
    cSetting_cartoon_highlight_color, cSetting_cartoon_side_chain_helper,
    cSetting_cartoon_smooth_loops, cSetting_cartoon_transparency,
    cSetting_cartoon_tube_radius, cSetting_cartoon_loop_radius,
    cSetting_cartoon_oval_length, cSetting_cartoon_oval_width,
    cSetting_cartoon_rect_length, cSetting_cartoon_rect_width,
    cSetting_cartoon_cylindrical_helices, cSetting_cartoon_debug,
    cSetting_cartoon_ring_mode, cSetting_cartoon_ladder_mode,
    cSetting_cartoon_nucleic_acid_mode, cSetting_cartoon_putty_radius,
    cSetting_cartoon_color, cSetting_ribbon_color, cSetting_ribbon_width,
    cSetting_sphere_scale, cSetting_sphere_color, cSetting_sphere_transparency,
    cSetting_stick_radius, cSetting_stick_color, cSetting_stick_transparency,
    cSetting_stick_ball, cSetting_stick_ball_ratio, cSetting_stick_ball_color,
    cSetting_valence, cSetting_line_width, cSetting_line_color,
    cSetting_ball_and_stick_scale, cSetting_ball_and_stick_bond_radius,
    cSetting_ball_and_stick_color,
    cSetting_dash_width, cSetting_dash_color, cSetting_dash_radius,
    cSetting_dash_gap, cSetting_dash_length, cSetting_mesh_color,
    cSetting_mesh_width, cSetting_dot_color, cSetting_surface_color,
    cSetting_surface_quality, cSetting_surface_type, cSetting_surface_mode,
    cSetting_solvent_radius, cSetting_transparency, cSetting_ray_transparency_oblique,
    cSetting_ray_transparency_oblique_power,
};

static bool SceneSettingIsColor(int index)
{
  return SettingGetType(index) == cSetting_color;
}

static bool SceneSettingKnown(int index)
{
  return index >= 0 && index < cSetting_INIT &&
         SettingGetType(index) != cSetting_blank;
}

/**
 * The value of a setting in `set`, false if it is not defined there. With
 * set == nullptr: the global value.
 */
static bool SceneSettingGet(PyMOLGlobals* G, const CSetting* set, int index,
    MovieSceneSetting& out)
{
  if (set && !set->info[index].defined)
    return false;
  if (!set)
    set = G->Setting;
  out.index = index;
  switch (SettingGetType(index)) {
  case cSetting_boolean:
  case cSetting_int:
  case cSetting_color:
    out.int_ = SettingGet<int>(index, set);
    break;
  case cSetting_float:
    out.float3_[0] = SettingGet<float>(index, set);
    break;
  case cSetting_float3:
    copy3f(SettingGet<const float*>(index, set), out.float3_);
    break;
  case cSetting_string:
    out.string_ = SettingGet<const char*>(index, set);
    break;
  default:
    return false;
  }
  return true;
}

static bool SceneSettingEqual(
    const MovieSceneSetting& a, const MovieSceneSetting& b)
{
  return a.int_ == b.int_ && a.string_ == b.string_ &&
         a.float3_[0] == b.float3_[0] && a.float3_[1] == b.float3_[1] &&
         a.float3_[2] == b.float3_[2];
}

static void SceneSettingSet(CSetting* set, const MovieSceneSetting& value)
{
  switch (SettingGetType(value.index)) {
  case cSetting_boolean:
  case cSetting_int:
  case cSetting_color:
    SettingSet_i(set, value.index, value.int_);
    break;
  case cSetting_float:
    SettingSet_f(set, value.index, value.float3_[0]);
    break;
  case cSetting_float3:
    SettingSet_3fv(set, value.index, value.float3_);
    break;
  case cSetting_string:
    SettingSet_s(set, value.index, value.string_.c_str());
    break;
  }
}

static bool SceneUniqueEqual(
    const SettingUniqueEntry& a, const SettingUniqueEntry& b)
{
  if (a.setting_id != b.setting_id)
    return false;
  switch (SettingGetType(a.setting_id)) {
  case cSetting_float:
    return a.value.float_ == b.value.float_;
  case cSetting_float3:
    return a.value.float3_[0] == b.value.float3_[0] &&
           a.value.float3_[1] == b.value.float3_[1] &&
           a.value.float3_[2] == b.value.float3_[2];
  }
  return a.value.int_ == b.value.int_;
}

/**
 * Give an atom or a bond the settings a scene stored for it and remove the
 * others; colors and the rest as asked. The ids of the settings that
 * changed go to `changed`.
 */
static void SceneUniqueRecall(PyMOLGlobals* G, int unique_id,
    const std::vector<SettingUniqueEntry>* stored, bool colors, bool others,
    std::set<int>& changed)
{
  auto wanted = [&](int id) {
    return SceneSettingKnown(id) && (SceneSettingIsColor(id) ? colors : others);
  };
  auto find = [](const std::vector<SettingUniqueEntry>& list, int id) {
    for (auto& entry : list)
      if (entry.setting_id == id)
        return &entry;
    return (const SettingUniqueEntry*) nullptr;
  };
  static const std::vector<SettingUniqueEntry> none;
  const auto& keep = stored ? *stored : none;
  const auto now = SettingUniqueGetEntries(G, unique_id);

  for (auto& entry : now) {
    if (wanted(entry.setting_id) && !find(keep, entry.setting_id)) {
      SettingUniqueUnset(G, unique_id, entry.setting_id);
      changed.insert(entry.setting_id);
    }
  }
  for (auto& entry : keep) {
    if (!wanted(entry.setting_id))
      continue;
    auto current = find(now, entry.setting_id);
    if (!current || !SceneUniqueEqual(*current, entry)) {
      SettingUniqueSetTypedValue(G, unique_id, entry.setting_id,
          SettingGetType(entry.setting_id), &entry.value);
      changed.insert(entry.setting_id);
    }
  }
}

/**
 * Fill scene.style for the atoms in scene.atomdata, the bonds between
 * them, the objects and the global level.
 */
static void MovieSceneStoreStyle(PyMOLGlobals* G, MovieScene& scene)
{
  auto& style = scene.style;
  style = MovieSceneStyle();
  std::set<int> colors; // the color indices the scene refers to

  auto note_color = [&](int index, int value) {
    if (SceneSettingIsColor(index))
      colors.insert(value);
  };

  for (ObjectIterator iter(G); iter.next();) {
    pymol::CObject* obj = iter.getObject();
    colors.insert(obj->Color);

    if (obj->Setting) {
      std::vector<MovieSceneSetting> defined;
      MovieSceneSetting value;
      for (int index : cSceneSettings) {
        if (SceneSettingGet(G, obj->Setting.get(), index, value)) {
          note_color(index, value.int_);
          defined.push_back(value);
        }
      }
      if (!defined.empty())
        style.object[obj->Name] = std::move(defined);
    }

    if (obj->type != cObjectMolecule)
      continue;
    auto mol = static_cast<ObjectMolecule*>(obj);
    auto stored = [&](int atm) {
      int id = mol->AtomInfo[atm].unique_id;
      return id && scene.atomdata.count(id);
    };
    auto keep = [&](int unique_id) {
      auto entries = SettingUniqueGetEntries(G, unique_id);
      for (auto& entry : entries)
        note_color(entry.setting_id, entry.value.int_);
      if (!entries.empty())
        style.unique[unique_id] = std::move(entries);
    };

    for (int atm = 0; atm < mol->NAtom; ++atm) {
      const AtomInfoType& ai = mol->AtomInfo[atm];
      if (!stored(atm))
        continue;
      colors.insert(ai.color);
      if (ai.cartoon)
        style.cartoon[ai.unique_id] = ai.cartoon;
      if (ai.has_setting)
        keep(ai.unique_id);
    }
    for (int b = 0; b < mol->NBond; ++b) {
      const BondType& bond = mol->Bond[b];
      if (bond.has_setting && bond.unique_id && stored(bond.index[0]) &&
          stored(bond.index[1]))
        keep(bond.unique_id);
    }
  }

  MovieSceneSetting value;
  for (int index : cSceneSettings) {
    if (SceneSettingGet(G, nullptr, index, value)) {
      note_color(index, value.int_);
      style.global.push_back(value);
    }
  }

  // the definitions of the named colors: one that is redefined later comes
  // back with the scene
  for (int color : colors) {
    if (color >= 0 && color < ColorGetNColor(G)) {
      const char* name = ColorGetName(G, color);
      const float* rgb = ColorGet(G, color);
      if (name && name[0])
        style.colors[name] = {rgb[0], rgb[1], rgb[2]};
    }
  }
}

/**
 * Store a scene
 *
 * @param name            name (key) of the scene to store or update
 *                  ("new"/empty = unique key)
 * @param message         wizard message to display with this scene
 * @param store_view      store the camera view
 * @param store_color     store colors
 * @param store_active    store enabled/disabled
 * @param store_rep       store reps
 * @param store_frame     store movie frame
 * @param store_thumbnail store the thumbnail
 */
pymol::Result<> MovieSceneStore(PyMOLGlobals * G, const char * name,
    const char * message,
    bool store_view,
    bool store_color,
    bool store_active,
    bool store_rep,
    bool store_frame,
    bool store_thumbnail,
    const char * sele,
    size_t stack,
    bool quiet,
    bool store_style)
{
  const bool is_defaultstack = stack == cMovieSceneStackDefault;
  // the style goes with the atoms' colors and reps; "undo" does without
  store_style &= is_defaultstack && (store_color || store_rep);
  auto scenes = G->scenes + stack;
  std::string key(name);

  if (is_defaultstack) {
    // new key?
    if (key.empty() || key == "new") {
      key = scenes->getUniqueKey();
      scenes->order.push_back(key);
    } else if (scenes->dict.find(key) == scenes->dict.end()) {
      scenes->order.push_back(key);
    }

    // set scene_current_name
    SettingSetGlobal_s(G, cSetting_scene_current_name, key.c_str());
  }

  MovieScene &scene = scenes->dict[key];

  // storemask
  scene.storemask = (
      (store_view ? STORE_VIEW : 0) |
      (store_active ? STORE_ACTIVE : 0) |
      (store_color ? STORE_COLOR : 0) |
      (store_rep ? STORE_REP : 0) |
      (store_frame ? STORE_FRAME : 0) |
      (store_thumbnail ? STORE_THUMBNAIL : 0) |
      (store_style ? STORE_STYLE : 0));

  // message
  scene.message = message ? message : "";

  // camera view
  SceneGetView(G, scene.view);

  // frame
  scene.frame = SceneGetFrame(G);

  // thumbnail
  if (store_thumbnail) {
    auto& thumbnailImage = scene.thumbnail;
    thumbnailImage.resize(MovieScene::THUMBNAIL_WIDTH, MovieScene::THUMBNAIL_HEIGHT);
    SceneUpdate(G, false); // Make sure scene is on screen
    Extent2D extent{static_cast<std::uint32_t>(thumbnailImage.getWidth()),
        static_cast<std::uint32_t>(thumbnailImage.getHeight())};
    SceneDeferImage(G, extent, nullptr, 0, -1, 0, 1, &thumbnailImage);
    SceneInvalidate(G); // Used to refresh the screen
  }

  // atomdata
  if (store_color || store_rep) {

    // fill atomdata dict
    for (SeleAtomIterator iter(G, sele); iter.next();) {

      // don't store atom data for disabled objects
      if (!((pymol::CObject*)iter.obj)->Enabled && is_defaultstack)
        continue;

      AtomInfoType * ai = iter.getAtomInfo();
      int unique_id = AtomInfoCheckUniqueID(G, ai);
      MovieSceneAtom &sceneatom = scene.atomdata[unique_id];

      sceneatom.color = ai->color;
      sceneatom.visRep = ai->visRep;
    }
  }

  scene.style = MovieSceneStyle();
  if (store_style)
    MovieSceneStoreStyle(G, scene);

  // objectdata
  for (ObjectIterator iter(G); iter.next();) {
    const SpecRec * rec = iter.getSpecRec();
    pymol::CObject * obj = iter.getObject();
    MovieSceneObject &sceneobj = scene.objectdata[obj->Name];

    sceneobj.color = obj->Color;
    sceneobj.visRep = obj->visRep;

    // store the "enabled" state in the first bit of visRep
    SET_BIT_TO(sceneobj.visRep, 0, rec->visible);
  }

  if (is_defaultstack && !quiet) {
    PRINTFB(G, FB_Scene, FB_Details)
    " scene: scene stored as \"%s\".\n", key.c_str() ENDFB(G);
  }

  return {};
}

pymol::Result<MovieScene> MovieSceneStoreNoStore(PyMOLGlobals* G,
    pymol::zstring_view name, pymol::null_safe_zstring_view message, bool store_view,
    bool store_color, bool store_active, bool store_rep, bool store_frame,
    bool store_thumbnail, pymol::zstring_view sele)
{
  std::string key{name.c_str()};

  MovieScene scene{};

  // storemask
  scene.storemask = (
      (store_view ? STORE_VIEW : 0) |
      (store_active ? STORE_ACTIVE : 0) |
      (store_color ? STORE_COLOR : 0) |
      (store_rep ? STORE_REP : 0) |
      (store_frame ? STORE_FRAME : 0) |
      (store_thumbnail ? STORE_THUMBNAIL : 0));

  // message
  scene.message = message.c_str();

  // camera view
  SceneGetView(G, scene.view);

  // frame
  scene.frame = SceneGetFrame(G);

  // thumbnail
  if (store_thumbnail) {
    // Preserve event by just resizing the thumbnail
    auto& thumbnailImage = scene.thumbnail;
    thumbnailImage.resize(
        MovieScene::THUMBNAIL_WIDTH, MovieScene::THUMBNAIL_HEIGHT);
    SceneUpdate(G, false); // Make sure scene is on screen
    Extent2D extent{static_cast<std::uint32_t>(thumbnailImage.getWidth()),
        static_cast<std::uint32_t>(thumbnailImage.getHeight())};
    SceneDeferImage(G, extent, nullptr, 0, -1, 0, 1, &thumbnailImage);
    SceneInvalidate(G); // Used to refresh the screen
  }

  // atomdata
  if (store_color || store_rep) {

    // fill atomdata dict
    for (SeleAtomIterator iter(G, sele.c_str()); iter.next();) {
      // // don't store atom data for disabled objects
      // if (!((pymol::CObject*)iter.obj)->Enabled && is_defaultstack)
      //   continue;

      AtomInfoType * ai = iter.getAtomInfo();
      int unique_id = AtomInfoCheckUniqueID(G, ai);
      MovieSceneAtom &sceneatom = scene.atomdata[unique_id];

      sceneatom.color = ai->color;
      sceneatom.visRep = ai->visRep;
    }
  }

  // objectdata
  for (ObjectIterator iter(G); iter.next();) {
    const SpecRec * rec = iter.getSpecRec();
    pymol::CObject * obj = iter.getObject();
    MovieSceneObject &sceneobj = scene.objectdata[obj->Name];

    sceneobj.color = obj->Color;
    sceneobj.visRep = obj->visRep;

    // store the "enabled" state in the first bit of visRep
    SET_BIT_TO(sceneobj.visRep, 0, rec->visible);
  }

  return scene;
}

/**
 * Display a message (with the message wizard)
 */
static void MovieSceneRecallMessage(PyMOLGlobals * G, const std::string &message)
{
  // we can't just call python functions because we might be in the wrong
  // thread. Instead, pass a parsable python string to PParse.
  // To avoid syntax errors, replace all single quotes in *message*.

  std::string pystr = "/cmd.scene_recall_message(r'''" + message + "''')";
  std::replace(pystr.begin() + 30, pystr.end() - 4, '\'', '`');
  PParse(G, pystr.c_str());
}

/**
 * Get message for a scene based on name
 * @param name name of the scene
 */
std::string MovieSceneGetMessage(PyMOLGlobals* G, pymol::zstring_view name)
{
  auto scenes = G->scenes + cMovieSceneStackDefault;
  auto it = scenes->dict.find(name.c_str());

  if (it == scenes->dict.end()) {
    return {};
  }

  return it->second.message;
}

/**
 * Set message for a scene based on name
 * @param name name of the scene
 * @param message scene's message
 */
pymol::Result<> MovieSceneSetMessage(
    PyMOLGlobals* G, pymol::zstring_view name, pymol::zstring_view message)
{
  auto scenes = G->scenes + cMovieSceneStackDefault;
  auto it = scenes->dict.find(name.c_str());

  if (it == scenes->dict.end()) {
    return pymol::make_error(name, " could not be found.");
  } else {
    it->second.message = message.c_str();
    return {};
  }
}

/**
 * Set the frame or state, depending on whether a movie is defined and/or
 * playing, and depending on the scene_frame_mode setting.
 */
static void MovieSceneRecallFrame(PyMOLGlobals * G, int frame)
{
  int mode = 4;

  if (MoviePlaying(G)) {
    mode = 10; // seek scene
  } else if (frame == SceneGetFrame(G)) {
    return;
  } else {
    int scene_frame_mode = SettingGetGlobal_i(G, cSetting_scene_frame_mode);
    if(scene_frame_mode == 0 || (scene_frame_mode < 0 && MovieDefined(G)))
      return;
  }

  // PBlock fails with SceneSetFrame. Workaround: call from Python
  PXDecRef(PYOBJECT_CALLMETHOD(G->P_inst->cmd, "set_frame", "ii", frame + 1, mode));
}

/**
 * Scene animation duration from settings
 */
static float get_scene_animation_duration(PyMOLGlobals * G) {
  auto enabled = SettingGetGlobal_i(G, cSetting_scene_animation);
  if (enabled < 0)
    enabled = SettingGetGlobal_b(G, cSetting_animation);

  if (!enabled)
    return 0.f;

  return SettingGetGlobal_f(G, cSetting_scene_animation_duration);
}

pymol::Result<> MovieSceneRecallAllInstant(PyMOLGlobals * G, pymol::zstring_view name,
    std::size_t stack)
{
  return MovieSceneRecall(
      G, name.c_str(), 0.0f, true, true, true, true, true, "all", stack);
}

/**
 * Recall a scene
 *
 * @param name            name (key) of the scene to recall
 * @param animate         animation duration, use scene_animation_duration if -1
 * @param store_view      restore the camera view
 * @param store_color     restore colors
 * @param store_active    restore enabled/disabled
 * @param store_rep       restore reps
 * @return False if no scene named `name` exists
 */
pymol::Result<> MovieSceneRecall(PyMOLGlobals * G, const char * name, float animate,
    bool recall_view,
    bool recall_color,
    bool recall_active,
    bool recall_rep,
    bool recall_frame,
    const char * sele,
    size_t stack,
    bool recall_style)
{
  auto scenes = G->scenes + stack;
  auto it = scenes->dict.find(name);

  if (it == scenes->dict.end()) {
    return pymol::make_error("Scene ", name, " is not defined.");
  }

  if (stack == cMovieSceneStackDefault) {
    // set scene_current_name
    SettingSetGlobal_s(G, cSetting_scene_current_name, name);
  }

  const MovieScene &scene = it->second;
  MovieSceneRecallImpl(G, scene, animate, recall_view, recall_color,
      recall_active, recall_rep, recall_frame, sele, recall_style);
  return {};
}

pymol::Result<> MovieSceneRecallImpl(PyMOLGlobals* G, const MovieScene& scene,
    float animate, bool recall_view, bool recall_color, bool recall_active,
    bool recall_rep, bool recall_frame, const char* sele, bool recall_style)
{

  // recall features if requested and stored
  recall_view &= (scene.storemask & STORE_VIEW) != 0;
  recall_active &= (scene.storemask & STORE_ACTIVE) != 0;
  recall_color &= (scene.storemask & STORE_COLOR) != 0;
  recall_rep &= (scene.storemask & STORE_REP) != 0;
  recall_frame &= (scene.storemask & STORE_FRAME) != 0;
  // a scene stored before 4.47 has no style: nothing of it is touched
  recall_style &= (scene.storemask & STORE_STYLE) != 0;
  const MovieSceneStyle& style = scene.style;

  // keep track of changes
  // (obj -> repbitmask) stores the rep bits for all reps that changed,
  // a value of zero means just to invalidate color.
  std::map<pymol::CObject*, int> objectstoinvalidate;
  // (obj -> setting ids) of atoms and bonds; objects with a new cartoon type
  std::map<pymol::CObject*, std::set<int>> uniquechanged;
  std::set<pymol::CObject*> cartoonchanged;

  auto stored_unique = [&](int unique_id) {
    auto it = style.unique.find(unique_id);
    return it == style.unique.end() ? nullptr : &it->second;
  };

  if (recall_style && recall_color) {
    // a named color that was redefined since: back to what it was
    for (auto& item : style.colors) {
      int index = ColorGetIndex(G, item.first.c_str());
      if (index < 0 || item.second.size() != 3)
        continue;
      if (!within3f(ColorGet(G, index), item.second.data(), 1e-4f))
        ColorDef(G, item.first.c_str(), item.second.data(), 0, true);
    }
  }

  if (recall_style) {
    MovieSceneSetting now;
    for (auto& value : style.global) {
      if (!SceneSettingKnown(value.index) ||
          (SceneSettingIsColor(value.index) && !recall_color))
        continue;
      if (SceneSettingGet(G, nullptr, value.index, now) &&
          !SceneSettingEqual(now, value)) {
        SceneSettingSet(G->Setting, value);
        SettingGenerateSideEffects(G, value.index, nullptr, -1, true);
      }
    }
  }

  // atomdata
  if (recall_color || recall_rep) {

    // fill atomdata dict
    for (SeleAtomIterator iter(G, sele); iter.next();) {
      AtomInfoType * ai = iter.getAtomInfo();
      auto it = scene.atomdata.find(ai->unique_id);
      if (it == scene.atomdata.end())
        continue;

      const MovieSceneAtom &sceneatom = it->second;

      if (recall_style) {
        if (recall_rep) {
          auto found = style.cartoon.find(ai->unique_id);
          int cartoon = found == style.cartoon.end() ? 0 : found->second;
          if (ai->cartoon != cartoon) {
            ai->cartoon = cartoon;
            cartoonchanged.insert(iter.obj);
          }
        }
        auto stored = stored_unique(ai->unique_id);
        if (stored || ai->has_setting) {
          SceneUniqueRecall(G, ai->unique_id, stored, recall_color, recall_rep,
              uniquechanged[iter.obj]);
          if (stored)
            ai->has_setting = true;
        }
      }

      if (recall_color) {
        if (ai->color != sceneatom.color)
          objectstoinvalidate[iter.obj];

        ai->color = sceneatom.color;
      }

      if (recall_rep) {
        int changed = (ai->visRep ^ sceneatom.visRep) & cRepsAtomMask;
        if (changed)
          objectstoinvalidate[iter.obj] |= changed;

        ai->visRep = sceneatom.visRep;
      }
    }
  }

  // disable all objects
  if (recall_active) {
    // need to control SpecRec
    ExecutiveSetObjVisib(G, "*", false, false);
  }

  // objectdata
  for (ObjectIterator iter(G); iter.next();) {
    pymol::CObject * obj = iter.getObject();
    auto it = scene.objectdata.find(obj->Name);
    if (it == scene.objectdata.end())
      continue;

    const MovieSceneObject &sceneobj = it->second;

    if (recall_style) {
      // settings of the object: the stored ones, and none of the others
      auto found = style.object.find(obj->Name);
      MovieSceneSetting now;
      for (int index : cSceneSettings) {
        if (SceneSettingIsColor(index) ? !recall_color : !recall_rep)
          continue;
        const MovieSceneSetting* want = nullptr;
        if (found != style.object.end()) {
          for (auto& value : found->second)
            if (value.index == index)
              want = &value;
        }
        bool defined =
            obj->Setting && SceneSettingGet(G, obj->Setting.get(), index, now);
        if (want && !(defined && SceneSettingEqual(now, *want))) {
          SettingCheckHandle(G, obj->Setting);
          SceneSettingSet(obj->Setting.get(), *want);
        } else if (!want && defined) {
          SettingUnset(obj->Setting.get(), index);
        } else {
          continue;
        }
        SettingGenerateSideEffects(G, index, obj->Name, -1, true);
      }

      // bonds between atoms of the scene
      if (obj->type == cObjectMolecule && (recall_color || recall_rep)) {
        auto mol = static_cast<ObjectMolecule*>(obj);
        auto sele_id = SelectorIndexByName(G, sele);
        auto in_scene = [&](int atm) {
          const AtomInfoType& ai = mol->AtomInfo[atm];
          return ai.unique_id && scene.atomdata.count(ai.unique_id) &&
                 SelectorIsMember(G, ai.selEntry, sele_id);
        };
        for (int b = 0; b < mol->NBond; ++b) {
          BondType& bond = mol->Bond[b];
          auto stored = bond.unique_id ? stored_unique(bond.unique_id) : nullptr;
          if ((stored || bond.has_setting) && bond.unique_id &&
              in_scene(bond.index[0]) && in_scene(bond.index[1])) {
            SceneUniqueRecall(G, bond.unique_id, stored, recall_color,
                recall_rep, uniquechanged[obj]);
            if (stored)
              bond.has_setting = true;
          }
        }
      }
    }

    if (recall_color) {
      if (obj->Color != sceneobj.color)
        objectstoinvalidate[obj];

      obj->Color = sceneobj.color;
    }

    if (recall_rep) {
      int changed = (obj->visRep ^ sceneobj.visRep) & cRepsObjectMask;
      if (changed)
        objectstoinvalidate[obj] |= changed;

      obj->visRep = sceneobj.visRep;
    }

    // "enabled" state is first bit in visRep
    int enabled = GET_BIT(sceneobj.visRep, 0);
    if(recall_active && enabled) {
      // need to control SpecRec
      ExecutiveSetObjVisib(G, obj->Name, enabled, false);
    }
  }

  // invalidate
  for (auto& item : objectstoinvalidate) {
    item.first->invalidate(cRepAll, item.second ? cRepInvVisib : cRepInvColor, -1);
  }
  for (auto obj : cartoonchanged) {
    obj->invalidate(cRepCartoon, cRepInvRep, -1);
  }
  for (auto& item : uniquechanged) {
    for (int index : item.second)
      SettingGenerateSideEffects(G, index, item.first->Name, -1, true);
  }

  // camera view
  if (recall_view) {
    if (animate < -0.5) // == -1
      animate = get_scene_animation_duration(G);

    SceneSetView(G, scene.view, true, animate, 1);
  }

  // message
  MovieSceneRecallMessage(G, scene.message);

  // frame
  if (recall_frame) {
    MovieSceneRecallFrame(G, scene.frame);
  }

  return {};
}

/**
 * Rename or delete a scene
 *
 * @param name name to rename or delete, or "*" to delete all
 * @param new_name new scene name to rename, or nullptr to delete
 */
pymol::Result<> MovieSceneRename(PyMOLGlobals * G, const char * name, const char * new_name) {

  if (strcmp(name, "*") == 0) {
    // delete all scenes
    G->scenes->dict.clear();
    G->scenes->order.clear();
    return {};
  }

  if (!new_name) {
    new_name = "";
  } else if (strcmp(name, new_name) == 0) {
    return {};
  }

  auto it = G->scenes->dict.find(name);

  if (it != G->scenes->dict.end()) {
    if (new_name[0])
      std::swap(G->scenes->dict[new_name], it->second);
    G->scenes->dict.erase(it);

    // does a scene named "new_name" already exist?
    auto old_new = std::find(G->scenes->order.begin(), G->scenes->order.end(), new_name);

    // replace in or remove from "G->scenes->order" list
    auto v_it = std::find(G->scenes->order.begin(), G->scenes->order.end(), name);
    if (v_it == G->scenes->order.end()) {
      printf("this is a bug, name must be in G->scenes->order\n");
    } else {
      if (new_name[0]) {
        // rename
        v_it->assign(new_name);

        // overwritten existing key?
        if (old_new != G->scenes->order.end())
          G->scenes->order.erase(old_new);
      } else {
        // remove
        G->scenes->order.erase(v_it);
      }
    }

    // update scene_current_name
    if (0 == strcmp(name, SettingGetGlobal_s(G,
            cSetting_scene_current_name))) {
      SettingSetGlobal_s(G, cSetting_scene_current_name, new_name);
    }

    return {};
  }

  return pymol::make_error(name, " could not be found.");
}

/**
 * Delete a scene
 *
 * @param name scene name or "*" to delete all scenes (for default stack)
 */
pymol::Result<> MovieSceneDelete(PyMOLGlobals* G, const char* name, size_t stack) {
  if (stack != cMovieSceneStackDefault) {
    if(G->scenes[stack].dict.erase(name) != 0) {
      return {};
    }
    return pymol::make_error(name, " not found.");
  }

  // takes also care of scene order and name="*"
  return MovieSceneRename(G, name, nullptr);
}

/**
 * Print current scene order
 */
static pymol::Result<> MovieScenePrintOrder(PyMOLGlobals * G) {
  PRINTFB(G, FB_Scene, FB_Details)
    " scene: current order:\n" ENDFB(G);

  for (auto it = G->scenes->order.begin(); it != G->scenes->order.end(); ++it) {
    PRINTFB(G, FB_Scene, FB_Details)
      " %s", it->c_str() ENDFB(G);
  }

  PRINTFB(G, FB_Scene, FB_Details)
    "\n" ENDFB(G);

  return {};
}

/**
 * Based on the "scene_current_name" setting, get the next or previous key.
 *
 * If the "scene_loop" setting is false and the key is out of range, return
 * an empty string.
 *
 * @param next true = next, false = previous
 */
static const char * MovieSceneGetNextKey(PyMOLGlobals * G, bool next) {
  const char * current_name = SettingGetGlobal_s(G, cSetting_scene_current_name);
  int scene_loop = SettingGetGlobal_b(G, cSetting_scene_loop);

  if (!current_name[0])
    scene_loop = true;

  auto it = std::find(G->scenes->order.begin(), G->scenes->order.end(), current_name);

  if (next) {
    if (it < G->scenes->order.end() - 1) {
      ++it;
    } else if (scene_loop) {
      it = G->scenes->order.begin();
    } else {
      return "";
    }
  } else {
    if (it != G->scenes->order.begin() && it != G->scenes->order.end()) {
      --it;
    } else if (scene_loop) {
      it = G->scenes->order.end() - 1;
    } else {
      return "";
    }
  }

  return it->c_str();
}

/**
 * Move the current scene (scene_current_name) before or after "key"
 */
static pymol::Result<> MovieSceneOrderBeforeAfter(PyMOLGlobals * G, const char * key, bool before)
{
  const char * location = nullptr;
  const char * key2 = SettingGetGlobal_s(G, cSetting_scene_current_name);

  if (before) {
    auto it = std::find(G->scenes->order.begin(), G->scenes->order.end(), key);
    if (it == G->scenes->order.begin()) {
      location = "top";
      key = "";
    } else {
      key = (it - 1)->c_str();
    }
  }

  MovieSceneOrder(G, std::vector<std::string>{key, key2}, false, location);
  return {};
}

/**
 * C implementation of the "scene" command
 */
pymol::Result<> MovieSceneFunc(PyMOLGlobals* G, const MovieSceneFuncArgs& args)
{
  auto scenes = G->scenes + args.stack;
  std::string prev_name;
  short beforeafter = 0;
  pymol::Result<> status;
  pymol::zstring_view action = args.action;
  pymol::zstring_view key = args.key;

  PRINTFB(G, FB_Scene, FB_Blather)
    " MovieScene: key=%s action=%s message=%s store_view=%d store_color=%d"
    " store_active=%d store_rep=%d store_thumbnail=%d animate=%f new_key=%s hand=%d\n",
    key.c_str(), action.c_str(), args.message.c_str(), args.store_view, args.store_color, args.store_active,
    args.store_rep, args.store_thumbnail, args.animate, args.new_key.c_str(), args.hand
    ENDFB(G);

  // insert_before, insert_after
  if (action.starts_with("insert_")) {
    prev_name = SettingGetGlobal_s(G, cSetting_scene_current_name);
    if (!prev_name.empty())
      beforeafter = (action[7] == 'b') ? 1 : 2;
    action = "store";
  }

  if (action == "next" || action == "previous") {
    ok_assert(NOSCENES, scenes->order.size());

    key = MovieSceneGetNextKey(G, action[0] == 'n');
    action = "recall";
  } else if (action == "start") {
    ok_assert(NOSCENES, scenes->order.size());

    key = scenes->order[0];
    action = "recall";
  } else if (key == "auto") {
    key = SettingGetGlobal_s(G, cSetting_scene_current_name);
  }

  if (action == "recall") {
    if (key == "*")
      return MovieScenePrintOrder(G);

    if (!key[0]) {
      // empty key -> put up blank screen
      SettingSetGlobal_s(G, cSetting_scene_current_name, "");
      ExecutiveSetObjVisib(G, "*", false, false);
      MovieSceneRecallMessage(G, "");
    } else {
      status = MovieSceneRecall(G, key.c_str(), args.animate, args.store_view,
      args.store_color, args.store_active, args.store_rep, args.store_frame,
      args.sele.c_str(), args.stack, args.store_style);
    }

  } else if (action == "store") {
    status = MovieSceneStore(G, key.c_str(), args.message.c_str(), args.store_view,
    args.store_color, args.store_active, args.store_rep, args.store_frame, args.store_thumbnail,
    args.sele.c_str(), args.stack, args.quiet, args.store_style);

    // insert_before, insert_after
    if (status && beforeafter)
      status = MovieSceneOrderBeforeAfter(G, prev_name.c_str(), beforeafter == 1);

  } else if (action == "delete") {
    status = MovieSceneDelete(G, key.c_str(), args.stack);
  } else if (action == "rename") {
    status = MovieSceneRename(G, key.c_str(), args.new_key.c_str());
  } else if (action == "order") {
    status = MovieSceneOrder(G, key.c_str());
  } else if (action == "sort") {
    status = MovieSceneOrder(G, key.c_str(), true);
  } else if (action == "first") {
    status = MovieSceneOrder(G, key.c_str(), false, "top");
  } else {
    PRINTFB(G, FB_Scene, FB_Errors)
      " Error: invalid action '%s'\n", action.c_str() ENDFB(G);
  }

  // trigger GUI updates (scene buttons, Tcl/Tk menu)
  SettingSet<bool>(G, cSetting_scenes_changed, true);
  SettingGenerateSideEffects(G, cSetting_scenes_changed, nullptr, 0, true);

  return status;

ok_exceptNOSCENES:
  return pymol::make_error("No scenes");
}

/*
 * Init/Free to set up PyMOLGlobals in PyMOL_Start
 */

void MovieScenesInit(PyMOLGlobals * G) {
  MovieScenesFree(G);
  G->scenes = new CMovieScenes[cMovieSceneStack_SIZE];
}

void MovieScenesFree(PyMOLGlobals * G) {
  if (G->scenes) {
    delete[] G->scenes;
    G->scenes = nullptr;
  }
}

/*
 * PConvToPyObject/PConvFromPyObject
 *
 * Convertion to/from Python objects for all MovieScene types
 */

static PyObject * PConvToPyObject(const MovieSceneAtom &v) {
  return PConvArgsToPyList(v.color, v.visRep);
}

static PyObject * PConvToPyObject(const MovieSceneObject &v) {
  return PConvArgsToPyList(v.color, v.visRep);
}

/*
 * The value of a setting as int, float, [float, float, float] or str, by
 * the type of the setting.
 */
static PyObject* SceneValueAsPy(int index, int i, const float* f, const char* s)
{
  switch (SettingGetType(index)) {
  case cSetting_float:
    return PyFloat_FromDouble(f[0]);
  case cSetting_float3:
    return PConvFloatArrayToPyList(f, 3);
  case cSetting_string:
    return PyUnicode_FromString(s);
  }
  return PyLong_FromLong(i);
}

static bool SceneValueFromPy(
    int index, PyObject* value, int& i, float* f, std::string* s)
{
  if (!SceneSettingKnown(index) || !value)
    return false; // of a newer version
  switch (SettingGetType(index)) {
  case cSetting_float:
    f[0] = (float) PyFloat_AsDouble(value);
    break;
  case cSetting_float3:
    if (!PyList_Check(value) || PyList_Size(value) != 3)
      return false;
    for (int k = 0; k < 3; ++k)
      f[k] = (float) PyFloat_AsDouble(PyList_GetItem(value, k));
    break;
  case cSetting_string:
    if (!s || !PyUnicode_Check(value))
      return false;
    *s = PyUnicode_AsUTF8(value);
    break;
  default:
    i = (int) PyLong_AsLong(value);
  }
  if (PyErr_Occurred()) {
    PyErr_Clear();
    return false;
  }
  return true;
}

static PyObject* SceneSettingsAsPy(const std::vector<MovieSceneSetting>& list)
{
  PyObject* out = PyList_New(list.size());
  for (size_t k = 0; k < list.size(); ++k) {
    auto& v = list[k];
    PyList_SET_ITEM(out, k,
        Py_BuildValue("iN", v.index,
            SceneValueAsPy(v.index, v.int_, v.float3_, v.string_.c_str())));
  }
  return out;
}

static void SceneSettingsFromPy(
    PyObject* list, std::vector<MovieSceneSetting>& out)
{
  for (Py_ssize_t k = 0; list && PyList_Check(list) && k < PyList_Size(list);
       ++k) {
    PyObject* item = PyList_GetItem(list, k);
    MovieSceneSetting v;
    if (PyTuple_Check(item) && PyTuple_Size(item) == 2 &&
        PyLong_Check(PyTuple_GetItem(item, 0))) {
      v.index = (int) PyLong_AsLong(PyTuple_GetItem(item, 0));
      if (SceneValueFromPy(v.index, PyTuple_GetItem(item, 1), v.int_,
              v.float3_, &v.string_))
        out.push_back(v);
    }
  }
}

/*
 * [cartoon {id: type}, unique {id: [(setting, value)]},
 *  object {name: [(setting, value)]}, global [(setting, value)],
 *  colors {name: [r, g, b]}]
 */
static PyObject* PConvToPyObject(const MovieSceneStyle& v)
{
  PyObject* unique = PyDict_New();
  for (auto& item : v.unique) {
    PyObject* list = PyList_New(item.second.size());
    for (size_t k = 0; k < item.second.size(); ++k) {
      auto& e = item.second[k];
      PyList_SET_ITEM(list, k,
          Py_BuildValue("iN", e.setting_id,
              SceneValueAsPy(e.setting_id, e.value.int_, e.value.float3_, "")));
    }
    PyObject* key = PyLong_FromLong(item.first);
    PyDict_SetItem(unique, key, list);
    Py_DECREF(key);
    Py_DECREF(list);
  }
  PyObject* cartoon = PyDict_New();
  for (auto& item : v.cartoon) {
    PyObject* key = PyLong_FromLong(item.first);
    PyObject* value = PyLong_FromLong(item.second);
    PyDict_SetItem(cartoon, key, value);
    Py_DECREF(key);
    Py_DECREF(value);
  }
  PyObject* object = PyDict_New();
  for (auto& item : v.object) {
    PyObject* list = SceneSettingsAsPy(item.second);
    PyDict_SetItemString(object, item.first.c_str(), list);
    Py_DECREF(list);
  }
  PyObject* colors = PyDict_New();
  for (auto& item : v.colors) {
    PyObject* rgb = PConvFloatArrayToPyList(item.second.data(), item.second.size());
    PyDict_SetItemString(colors, item.first.c_str(), rgb);
    Py_DECREF(rgb);
  }
  return Py_BuildValue(
      "[NNNNN]", cartoon, unique, object, SceneSettingsAsPy(v.global), colors);
}

static void PConvFromPyObject(PyMOLGlobals* G, PyObject* obj, MovieSceneStyle& out)
{
  out = MovieSceneStyle();
  if (!obj || !PyList_Check(obj) || PyList_Size(obj) < 5)
    return;
  PyObject *key, *value;
  Py_ssize_t pos = 0;
  PyObject* cartoon = PyList_GetItem(obj, 0);
  while (PyDict_Check(cartoon) && PyDict_Next(cartoon, &pos, &key, &value)) {
    if (PyLong_Check(key) && PyLong_Check(value))
      out.cartoon[SettingUniqueConvertOldSessionID(G, (int) PyLong_AsLong(key))] =
          (int) PyLong_AsLong(value);
  }
  pos = 0;
  PyObject* unique = PyList_GetItem(obj, 1);
  while (PyDict_Check(unique) && PyDict_Next(unique, &pos, &key, &value)) {
    if (!PyLong_Check(key) || !PyList_Check(value))
      continue;
    std::vector<SettingUniqueEntry> entries;
    for (Py_ssize_t k = 0; k < PyList_Size(value); ++k) {
      PyObject* item = PyList_GetItem(value, k);
      SettingUniqueEntry e{};
      if (PyTuple_Check(item) && PyTuple_Size(item) == 2 &&
          PyLong_Check(PyTuple_GetItem(item, 0))) {
        e.setting_id = (int) PyLong_AsLong(PyTuple_GetItem(item, 0));
        if (SceneValueFromPy(e.setting_id, PyTuple_GetItem(item, 1),
                e.value.int_, e.value.float3_, nullptr))
          entries.push_back(e);
      }
    }
    if (!entries.empty())
      out.unique[SettingUniqueConvertOldSessionID(G, (int) PyLong_AsLong(key))] =
          std::move(entries);
  }
  pos = 0;
  PyObject* object = PyList_GetItem(obj, 2);
  while (PyDict_Check(object) && PyDict_Next(object, &pos, &key, &value)) {
    if (PyUnicode_Check(key))
      SceneSettingsFromPy(value, out.object[PyUnicode_AsUTF8(key)]);
  }
  SceneSettingsFromPy(PyList_GetItem(obj, 3), out.global);
  pos = 0;
  PyObject* colors = PyList_GetItem(obj, 4);
  while (PyDict_Check(colors) && PyDict_Next(colors, &pos, &key, &value)) {
    std::vector<float> rgb;
    if (PyUnicode_Check(key) && PConvFromPyObject(G, value, rgb) && rgb.size() == 3)
      out.colors[PyUnicode_AsUTF8(key)] = rgb;
  }
  if (PyErr_Occurred())
    PyErr_Clear();
}

static PyObject * PConvToPyObject(const MovieScene &v) {
  // a seventh item for the style; a reader that knows six ignores it
  const bool style = v.storemask & STORE_STYLE;
  PyObject * obj = PyList_New(style ? 7 : 6);
  if (style)
    PyList_SET_ITEM(obj, 6, PConvToPyObject(v.style));
  PyList_SET_ITEM(obj, 0, PConvToPyObject(v.storemask));
  PyList_SET_ITEM(obj, 1, PConvToPyObject(v.frame));
  PyList_SET_ITEM(obj, 2, PConvToPyObject(v.message.c_str()));
  PyList_SET_ITEM(obj, 3, PConvToPyObject(v.view, cSceneViewSize));
  PyList_SET_ITEM(obj, 4, PConvToPyObject(v.atomdata));
  PyList_SET_ITEM(obj, 5, PConvToPyObject(v.objectdata));
  return obj;
}

static bool PConvFromPyObject(PyMOLGlobals *, PyObject * obj, MovieSceneAtom &out) {
  return PConvArgsFromPyList(nullptr, obj, out.color, out.visRep);
}

static bool PConvFromPyObject(PyMOLGlobals *, PyObject * obj, MovieSceneObject &out) {
  return PConvArgsFromPyList(nullptr, obj, out.color, out.visRep);
}

static bool PConvFromPyObject(PyMOLGlobals * G, PyObject * obj, MovieScene &out) {
  std::map<int, MovieSceneAtom> atomdata_old_ids;

  if (!G) {
    printf(" Error: G is nullptr\n");
    return false;
  }

  if (!PConvArgsFromPyList(nullptr, obj, out.storemask, out.frame, out.message,
          out.view, atomdata_old_ids, out.objectdata)) {
    /* ignore */
  }

  // restore atomdata dict but with converted ids
  PConvFromPyObject(G, PyList_GetItem(obj, 4), atomdata_old_ids);
  for (auto& item : atomdata_old_ids) {
    int unique_id = SettingUniqueConvertOldSessionID(G, item.first);
    std::swap(out.atomdata[unique_id], item.second);
  }

  if (PyList_Size(obj) > 6) {
    PConvFromPyObject(G, PyList_GetItem(obj, 6), out.style);
  } else {
    out.storemask &= ~STORE_STYLE;
  }

  return true;
}

/*
 * For get_session
 */

PyObject * MovieScenesAsPyList(PyMOLGlobals * G) {
  return PConvArgsToPyList(G->scenes->order, G->scenes->dict);
}

void MovieScenesFromPyList(PyMOLGlobals * G, PyObject * o) {
  // delete existing scenes
  MovieSceneRename(G, "*");

  PConvArgsFromPyList(G, o, G->scenes->order, G->scenes->dict);
}

pymol::Result<MovieScene*> MovieSceneGet(
    PyMOLGlobals* G, pymol::zstring_view scene_name)
{
  auto it = G->scenes->dict.find(scene_name.c_str());
  if (it == G->scenes->dict.end()) {
    return pymol::make_error("Scene Name not found: ", scene_name);
  }
  return &G->scenes->dict[scene_name.c_str()];
}

// vi:sw=2:expandtab:cindent
