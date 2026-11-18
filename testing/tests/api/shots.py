"""
pymol.shots: a list of shots built into the movie of the core.
"""

from pymol import cmd, shots, testing


class TestShots(testing.PyMOLTestCase):
    def setUp(self):
        super().setUp()
        cmd.set("movie_fps", 30)
        cmd.fab("ACDEFGHIK", "pep")
        cmd.orient()

    def _view(self, frame):
        cmd.frame(frame)
        return [round(x, 2) for x in cmd.get_view()[:9]]

    def test_turn(self):
        self.assertEqual(shots.build([shots.shot("turn", "", 2)]), [1])
        self.assertEqual(cmd.get_movie_length(), 60)
        first, half, last = self._view(1), self._view(30), self._view(60)
        self.assertEqual(first, last)  # a full turn ends where it began
        self.assertAlmostEqual(first[0], -half[0], 1)  # half way: turned around
        # a quarter turn does not come back
        shots.build([shots.shot("turn", "", 2, angle=90)])
        self.assertNotEqual(self._view(1), self._view(60))

    def test_scenes_hold_cut(self):
        cmd.scene("a", "store")
        cmd.turn("x", 90)
        cmd.scene("b", "store")
        b = [round(x, 2) for x in cmd.get_view()[:9]]
        cmd.turn("x", -90)
        a = [round(x, 2) for x in cmd.get_view()[:9]]
        starts = shots.build(
            [
                shots.shot("scene", "a", 2),
                shots.shot("scene", "b", 6),
                shots.shot("hold", "", 1),
            ]
        )
        self.assertEqual(starts, [1, 61, 241])
        self.assertEqual(cmd.get_movie_length(), 270)
        self.assertEqual(self._view(1), a)
        self.assertEqual(self._view(60), a)  # a scene is held to its end
        flight = self._view(61 + 30)  # two seconds of flight, then b
        self.assertNotEqual(flight, a)
        self.assertNotEqual(flight, b)
        self.assertEqual(self._view(61 + 60), b)
        self.assertEqual(self._view(270), b)
        # a cut: b from the first frame of its shot
        cut = shots.shot("scene", "b", 6, start="cut")
        shots.build([shots.shot("scene", "a", 2), cut])
        self.assertEqual(self._view(61), b)

    def test_rock_nutate_states(self):
        cmd.create("pep", "pep", 1, 2)
        cmd.create("pep", "pep", 1, 3)
        starts = shots.build(
            [shots.shot(kind, "", 4) for kind in ("rock", "nutate", "states")]
        )
        self.assertEqual(starts, [1, 121, 241])
        rest = self._view(1)
        self.assertNotEqual(self._view(31), rest)  # swung out
        self.assertEqual(self._view(120), rest)  # and back
        self.assertNotEqual(self._view(121 + 24), rest)
        self.assertEqual(self._view(240), rest)
        cmd.frame(241)
        self.assertEqual(cmd.get_state(), 1)
        cmd.frame(360)
        self.assertEqual(cmd.get_state(), 3)

    def test_effect_and_clear(self):
        fade = shots.shot("hold", "", 1, effect="fade in surface")
        shots.build([fade])
        cmd.frame(30)
        cmd.frame(1)
        self.assertEqual(cmd.get_setting_float("transparency"), 1)
        cmd.frame(30)
        self.assertEqual(cmd.get_setting_float("transparency"), 0)
        # the next build has no trace of the fade
        shots.build([shots.shot("hold", "", 1)])
        cmd.set("transparency", 0.5)
        cmd.frame(30)
        cmd.frame(1)
        self.assertEqual(cmd.get_setting_float("transparency"), 0.5)
        self.assertEqual(shots.build([]), [])
        self.assertEqual(cmd.get_movie_length(), 0)

    def test_tour_view_describe(self):
        cmd.load(self.datafile("1oky-frag.pdb"), "frag")
        cmd.scene("s1", "store")
        cmd.select("mysele", "pep & resi 3")
        self.assertEqual([s["target"] for s in shots.tour("scenes")], ["s1"])
        chains = shots.tour("chains")
        self.assertEqual([s["kind"] for s in chains[:2]], ["zoom", "turn"])
        self.assertEqual(cmd.count_atoms(chains[0]["target"]) > 0, True)
        self.assertEqual(shots.tour("selections")[0]["target"], "mysele")
        self.assertRaises(ValueError, shots.tour, "nothing")
        view = shots.shot("view")
        self.assertEqual(view["view"], cmd.get_view())
        text = shots.describe([view, shots.shot("turn")])
        space = {}
        exec(text, space)  # the script builds the same movie
        self.assertEqual(cmd.get_movie_length(), 120 + 240)
        frames, seconds, size = shots.estimate(40, 30, ray=1)
        self.assertEqual(frames, 360)
        self.assertGreater(seconds, 0)
        self.assertGreater(size, 0)
