"""Run without PyMOL: python testing/tests/system/source_install.py.

Installers and compilers are stand-ins; these checks never install packages.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STUB = r"""#!INTERPRETER
import json, os, pathlib, sys
name = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
config = json.loads(os.environ['INSTALL_TEST_CONFIG'])
with open(os.environ['INSTALL_TEST_LOG'], 'a') as log:
    log.write(json.dumps([name, *args]) + '\n')
if name == 'uname':
    print(config.get('os', 'Linux') if args == ['-s'] else config.get('arch', 'x86_64'))
elif name in ('python', 'python3.13', 'python3.14', 'python3'):
    if args[:2] == ['-m', 'venv']:
        target = pathlib.Path(args[2])
        (target / 'bin').mkdir(parents=True)
        (target / 'pyvenv.cfg').write_text('test fixture')
        (target / 'bin/python').symlink_to(pathlib.Path(sys.argv[0]).resolve())
    elif args[:2] == ['-m', 'pip']:
        sys.exit(config.get('pip_failure', 0))
    else:
        sys.exit(0 if config.get('python', True) else 1)
elif name in ('dpkg-query', 'rpm'):
    if config.get('missing', False):
        sys.exit(1)
    print('install ok installed')
elif name == 'xcrun':
    sys.exit(0 if config.get('compiler', True) else 1)
elif name == 'sudo':
    sys.exit(config.get('failure', 0))
elif name in ('apt-get', 'dnf', 'pixi'):
    sys.exit(config.get('failure', 0))
elif name in ('curl', 'xcode-select'):
    sys.exit(config.get('failure', 0))
"""


@unittest.skipIf(os.name == "nt", "Bash entry point")
class UnixInstaller(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pymolish install ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.log = self.root / "commands.jsonl"
        self.config = {}
        self.os_release = self.root / "os-release"
        self.os_release.write_text("ID=ubuntu\nID_LIKE=debian\n")
        # Redirect only the OS metadata file; executable behavior is unchanged.
        script = (
            (ROOT / "install")
            .read_text()
            .replace("/etc/os-release", str(self.os_release))
        )
        # The fixture path has spaces, like the checkout under test.
        script = script.replace(str(self.os_release), '"' + str(self.os_release) + '"')
        (self.root / "install").write_text(script)
        (self.root / "pixi.toml").write_text((ROOT / "pixi.toml").read_text())
        for name in (
            "uname",
            "apt-cache",
            "dpkg-query",
            "rpm",
            "sudo",
            "apt-get",
            "dnf",
            "python3.13",
            "python3.14",
            "python3",
            "pixi",
            "xcrun",
            "xcode-select",
            "curl",
        ):
            path = self.bin / name
            path.write_text(STUB.replace("INTERPRETER", sys.executable))
            path.chmod(0o755)

    def run_install(self, *args, stdin=""):
        env = dict(os.environ, PATH=f"{self.bin}:/usr/bin:/bin")
        env["INSTALL_TEST_CONFIG"] = json.dumps(self.config)
        env["INSTALL_TEST_LOG"] = str(self.log)
        env["HOME"] = str(self.root / "home")
        return subprocess.run(
            ["/bin/bash", str(self.root / "install"), *args],
            check=False,
            cwd=self.root.parent,
            env=env,
            input=stdin,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
        )

    def commands(self):
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_preview_native_and_extras_has_no_mutations(self):
        self.config["missing"] = True
        result = self.run_install("--dry-run", "--extras=chem,fix,ai")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("apt-get install", result.stdout)
        self.assertIn("nlohmann-json3-dev", result.stdout)
        self.assertIn("json=True", result.stdout)
        self.assertIn("use-msgpackc=c++11", result.stdout)
        self.assertIn("Preview only", result.stdout)
        self.assertFalse((self.root / ".venv-install").exists())
        self.assertFalse(
            any(c[0] in ("sudo", "apt-get", "pixi") for c in self.commands())
        )

    def test_old_python_uses_pixi(self):
        self.config["python"] = False
        result = self.run_install("--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Pixi py313", result.stdout)
        self.assertIn("--manifest-path", result.stdout)
        self.assertIn("-e py313 python", result.stdout)
        self.assertNotIn("-m venv", result.stdout)

    def test_fedora_packages(self):
        self.os_release.write_text("ID=fedora\n")
        self.config["missing"] = True
        result = self.run_install("--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("dnf install", result.stdout)
        self.assertIn("glew-devel", result.stdout)
        self.assertNotIn("apt-get install", result.stdout)

    def test_mac_and_missing_compiler_preview(self):
        self.config.update(os="Darwin", arch="arm64", compiler=False)
        result = self.run_install("--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("xcode-select --install", result.stdout)
        self.assertIn("-e py313", result.stdout)
        self.assertFalse(any(c[0] == "xcode-select" for c in self.commands()))

    def test_unsupported_os_arch_and_options_stop(self):
        for config, args in (
            ({"os": "FreeBSD"}, ["--dry-run"]),
            ({"os": "Darwin", "arch": "x86_64"}, ["--dry-run"]),
            ({"python": False, "arch": "aarch64"}, ["--dry-run"]),
            ({}, ["--extras=dev"]),
            ({}, ["--extras=aichem"]),
            ({}, ["--unknown"]),
        ):
            with self.subTest(config=config, args=args):
                self.config = config
                result = self.run_install(*args)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertNotIn("pip install", result.stdout)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "normal-user flow")
    def test_decline_and_eof_do_not_install(self):
        self.config["missing"] = True
        for answer in ("n\n", ""):
            result = self.run_install(stdin=answer)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertFalse(
                any(c[0] in ("sudo", "apt-get", "pixi") for c in self.commands())
            )

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "normal-user flow")
    def test_failed_setup_preserves_exit_and_does_not_build(self):
        self.config.update(missing=True, failure=7)
        result = self.run_install("--yes")
        self.assertEqual(result.returncode, 7, result.stdout)
        self.assertNotIn("pip install", result.stdout)
        self.assertNotIn("Installed and checked", result.stdout)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "normal-user flow")
    def test_failed_pip_does_not_report_success(self):
        self.config["pip_failure"] = 9
        result = self.run_install("--yes")
        self.assertEqual(result.returncode, 9, result.stdout)
        self.assertNotIn("pip check", result.stdout)
        self.assertNotIn("Installed and checked", result.stdout)

    def test_missing_pixi_preview_does_not_download(self):
        self.config["python"] = False
        (self.bin / "pixi").unlink()
        result = self.run_install("--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("https://pixi.sh/install.sh", result.stdout)
        self.assertFalse(any(c[0] == "curl" for c in self.commands()))

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "normal-user flow")
    def test_rerun_preserves_environment_and_checks_install(self):
        result = self.run_install("--yes", "--extras=")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Installed and checked", result.stdout)
        marker = self.root / ".venv-install" / "keep.txt"
        marker.write_text("existing data")
        result = self.run_install("--yes")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(marker.read_text(), "existing data")
        self.assertEqual(sum(c[1:3] == ["-m", "venv"] for c in self.commands()), 1)
        self.assertIn("pip check", result.stdout)
        self.assertIn("p.cmd.fragment", result.stdout)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "normal-user flow")
    def test_existing_non_environment_is_untouched(self):
        target = self.root / ".venv-install"
        target.write_text("user data")
        result = self.run_install("--yes")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(target.read_text(), "user data")


@unittest.skipUnless(os.name == "nt", "Windows entry point")
class WindowsInstaller(unittest.TestCase):
    def test_preview_from_another_directory_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix="pymolish install ") as temp:
            root = Path(temp)
            shutil.copy(ROOT / "install.cmd", root)
            driver = root / "check.cmd"
            driver.write_text(
                '@echo off\ncall "%~dp0install.cmd" --dry-run --extras "chem,fix,ai"\n'
                "exit /b %errorlevel%\n"
            )
            result = subprocess.run(
                [os.environ["COMSPEC"], "/d", "/c", str(driver)],
                check=False,
                cwd=root.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn(".[chem,fix,ai]", result.stdout)
            self.assertIn(str(root / "pixi.toml"), result.stdout)
            self.assertIn("Preview only", result.stdout)
            self.assertFalse((root / ".pixi").exists())


if __name__ == "__main__":
    unittest.main()
