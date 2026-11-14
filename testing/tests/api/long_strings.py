"""
Text longer than the 1024-byte line buffers of the core is cut, not written
or read past the end. The CI job sanitize-Linux is what fails when it is not.
"""

from pymol import cmd, testing


class TestLongStrings(testing.PyMOLTestCase):
    def test_setting_echo(self):
        value = "a" * 3000
        cmd.feedback("enable", "setting", "actions")
        cmd.set("fetch_host", value, quiet=0)
        self.assertEqual(cmd.get("fetch_host"), value)

    def test_label2(self):
        # label2 uses the C label parser
        cmd.fragment("gly")
        for expression in ('"' + "b" * 1500 + '"', "c" * 1500):
            cmd.label2("all", expression)
            lengths = set()
            cmd.iterate(
                "all", "lengths.add(len(label))", space={"lengths": lengths, "len": len}
            )
            self.assertEqual(lengths, {1023})
