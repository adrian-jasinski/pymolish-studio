"""Native check: python windows_installer.py <setup.exe> <ISCC.exe>.

Refuses to touch an existing installation. CI runs this after packaging;
the regular Python suite skips it because it needs the finished installer.
"""

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UNINSTALL_KEY = (
    r"Software\Microsoft\Windows\CurrentVersion\Uninstall\pymolish-studio_is1"
)


def run(*args, **kwargs):
    return subprocess.run(args, check=True, timeout=300, **kwargs)


def check_installer(installer, compiler):
    import winreg

    def installed_version():
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY) as key:
                return winreg.QueryValueEx(key, "DisplayVersion")[0]
        except FileNotFoundError:
            return None

    shortcut = Path(os.environ["APPDATA"]) / (
        "Microsoft/Windows/Start Menu/Programs/pymolish-studio.lnk"
    )
    if installed_version() is not None or shortcut.exists():
        raise RuntimeError(
            "Run on a test account without an existing pymolish installation"
        )
    version = re.search(
        r'^#define _PyMOL_VERSION "(\d+\.\d+\.\d+)"',
        (ROOT / "layer0/Version.h").read_text(),
        re.MULTILINE,
    )[1]
    installer, compiler = Path(installer).resolve(), Path(compiler).resolve()
    assert installer.is_file() and compiler.is_file()
    flags = (
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES",
        "/NORESTART",
        "/SP-",
        "/RESTARTEXITCODE=42",
    )

    with tempfile.TemporaryDirectory(prefix="pymolish installer ") as temporary:
        work = Path(temporary)
        app = work / "Installed żółć" / "pymolish-studio"
        old_bundle = work / "old bundle"
        old_bundle.mkdir()
        # A tiny earlier payload tests a real version change and obsolete files.
        (old_bundle / "obsolete.dll").write_bytes(b"old payload")
        manifest = work / "old-files.txt"
        manifest.write_text("obsolete.dll\n", encoding="utf-8-sig")
        run(
            str(compiler),
            "/DAppVersion=0.0.1",
            f"/DBundleDir={old_bundle}",
            f"/DOutputDir={work}",
            f"/DPayloadManifest={manifest}",
            str(ROOT / "packaging/windows.iss"),
        )
        uninstaller = app / "unins000.exe"
        try:
            run(
                str(work / "pymolish-0.0.1-Windows-X64-setup.exe"),
                *flags,
                f"/DIR={app}",
                f"/LOG={work / 'install.log'}",
            )
            assert installed_version() == "0.0.1"
            assert shortcut.is_file()
            assert (app / "obsolete.dll").is_file()
            user_files = [app / "saved session.pse", app / "_internal/user plugin.py"]
            for path in user_files:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"keep user data")
            outside = app.parent / "outside.txt"
            outside.write_bytes(b"outside the application")
            # Modified metadata must not let upgrade cleanup escape {app}.
            with (app / ".pymolish-files").open("a", encoding="utf-8") as handle:
                handle.write(f"..\\outside.txt\n{outside}\n")

            # Omit /DIR on upgrade: Setup must remember the selected directory.
            run(str(installer), *flags, f"/LOG={work / 'upgrade.log'}")
            assert installed_version() == version
            assert not (app / "obsolete.dll").exists()
            assert (app / "pymolish.exe").is_file()
            assert shortcut.is_file()
            for path in user_files:
                assert path.read_bytes() == b"keep user data"
            assert outside.read_bytes() == b"outside the application"

            script = work / "smoke.py"
            script.write_text(
                "from pathlib import Path\n"
                "from pymol import cmd\n"
                "from pymol.Qt import QtCore, QtWidgets\n"
                "import numpy, rdkit, openmm, pdbfixer\n"
                f"assert cmd.get_version()[0] == {version!r}\n"
                "cmd.fragment('gly')\n"
                "atoms = cmd.count_atoms()\n"
                "assert atoms > 0\n"
                "for extension in ('pdb', 'cif', 'sdf', 'pse'):\n"
                "    name = 'molecule.' + extension\n"
                "    cmd.save(name)\n"
                "    cmd.reinitialize()\n"
                "    cmd.load(name)\n"
                "    assert cmd.count_atoms() == atoms\n"
                "cmd.png('molecule.png', width=64, height=64, ray=1)\n"
                "assert Path('molecule.png').read_bytes().startswith(b'\\x89PNG')\n"
                "Path('launch-ok').write_text('ok')\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            for key in (
                "PYTHONHOME",
                "PYTHONPATH",
                "PYMOL_PATH",
                "QT_PLUGIN_PATH",
                "QT_QPA_PLATFORM_PLUGIN_PATH",
            ):
                env.pop(key, None)
            # Do not let the build environment's DLLs rescue a broken bundle.
            env["PATH"] = os.path.join(os.environ["SystemRoot"], "System32")
            run(str(app / "pymolish.exe"), "-ckqy", str(script), cwd=work, env=env)
            assert (work / "launch-ok").read_text() == "ok"
            notices = app / "_internal/pymol/pymol_path"
            for name in ("LICENSE", "LICENSE-MIT", "licenses/LGPL-3.0.txt"):
                assert (notices / name).is_file()

            run(str(uninstaller), *flags, f"/LOG={work / 'uninstall.log'}")
            assert installed_version() is None
            assert not shortcut.exists()
            assert not (app / "pymolish.exe").exists()
            assert not (app / ".pymolish-files").exists()
            for path in user_files:
                assert path.read_bytes() == b"keep user data"
            assert outside.read_bytes() == b"outside the application"
        except Exception:
            for log in work.glob("*.log"):
                print(
                    f"\n{log.name}:\n"
                    + "\n".join(
                        log.read_text(
                            encoding="utf-8-sig", errors="replace"
                        ).splitlines()[-60:]
                    )
                )
            raise
        finally:
            if uninstaller.exists():
                run(str(uninstaller), *flags)
    print("Windows installer: install, upgrade, launch and uninstall passed.")


@unittest.skipUnless(
    sys.platform == "win32" and os.environ.get("PYMOLISH_TEST_INSTALLER"),
    "requires the finished Windows installer and an unused test account",
)
def test_windows_installer():
    check_installer(
        os.environ["PYMOLISH_TEST_INSTALLER"], os.environ["INNO_SETUP_COMPILER"]
    )


if __name__ == "__main__":
    if sys.platform != "win32" or len(sys.argv) != 3:
        raise SystemExit(
            "On Windows: python windows_installer.py <setup.exe> <ISCC.exe>"
        )
    check_installer(*sys.argv[1:])
