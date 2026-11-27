@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "root=%~dp0"
set "dry_run=0"
set "yes=0"
set "extras="
set "extras_set=0"
:args
if "%~1"=="" goto detected
if "%~1"=="--help" goto help
if "%~1"=="-h" goto help
if "%~1"=="--dry-run" (set "dry_run=1" & shift & goto args)
if "%~1"=="--yes" (set "yes=1" & shift & goto args)
if "%~1"=="--extras" (
    set "extras=%~2"
    set "extras_set=1"
    shift
    shift
    goto args
)
set "arg=%~1"
if "%arg:~0,9%"=="--extras=" (
    set "extras=%arg:~9%"
    set "extras_set=1"
    shift
    goto args
)
echo Unknown option. Use install.cmd --help.
exit /b 2
:detected
if not defined extras goto architecture
set "invalid=%extras:chem=%"
if defined invalid set "invalid=%invalid:fix=%"
if defined invalid set "invalid=%invalid:ai=%"
if defined invalid set "invalid=%invalid:,=%"
if defined invalid (echo Extras must be chem,fix,ai or empty. & exit /b 2)
for %%E in (%extras:,= %) do if not "%%E"=="chem" if not "%%E"=="fix" if not "%%E"=="ai" (echo Invalid extra: %%E & exit /b 2)
:architecture
set "arch=%PROCESSOR_ARCHITECTURE%"
if defined PROCESSOR_ARCHITEW6432 set "arch=%PROCESSOR_ARCHITEW6432%"
if /i not "%arch%"=="AMD64" (echo This installer supports Windows x64. See docs/install.md. & exit /b 1)
pushd "%root%" || exit /b 1
echo Installing pymolish from source on Windows x64, in .pixi/envs/py313.

set "vswhere=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
set "compiler="
if exist "%vswhere%" for /f "usebackq delims=" %%V in (`"%vswhere%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "compiler=%%V"
if defined compiler goto pixi
echo Visual Studio C++ Build Tools and a Windows SDK are required.
echo In Visual Studio Installer, select Desktop development with C++.
echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
if "%dry_run%"=="1" goto compiler_preview
if exist "%vswhere%" (
    echo Modify your installation to add that workload, then rerun install.cmd.
    goto failed
)
where winget >nul 2>nul || goto manual_compiler
call :confirm "Install Visual Studio 2022 Build Tools with winget?"
if errorlevel 1 goto failed
:compiler_preview
call :run winget install --exact --id Microsoft.VisualStudio.2022.BuildTools --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
if errorlevel 1 goto failed
if "%dry_run%"=="1" goto pixi
echo Finish the compiler installation and any requested restart, then rerun install.cmd.
goto failed
:manual_compiler
echo Install the C++ workload from the link above, then rerun install.cmd.
goto failed

:pixi
set "pixi="
for /f "delims=" %%P in ('where pixi 2^>nul') do if not defined pixi set "pixi=%%P"
if not defined pixi if exist "%USERPROFILE%\.pixi\bin\pixi.exe" set "pixi=%USERPROFILE%\.pixi\bin\pixi.exe"
if defined pixi goto build
echo Pixi supplies Python and native libraries. https://pixi.sh
if "%dry_run%"=="1" goto pixi_preview
where winget >nul 2>nul || goto manual_pixi
call :confirm "Install Pixi with winget?"
if errorlevel 1 goto failed
:pixi_preview
call :run winget install --exact --id prefix-dev.pixi
if errorlevel 1 goto failed
if "%dry_run%"=="1" (set "pixi=pixi" & goto build)
echo Pixi installed. Open a new terminal in this folder and rerun install.cmd.
goto failed
:manual_pixi
echo Install Pixi from https://pixi.sh, open a new terminal and rerun install.cmd.
goto failed

:build
if "%extras_set%%yes%%dry_run%"=="000" (
    call :confirm "Include chemistry, structure repair and Chat libraries (chem,fix,ai)?"
    if not errorlevel 1 set "extras=chem,fix,ai"
)
set "target=."
if defined extras set "target=.[%extras%]"
call :run "%pixi%" run -e py313 python -m pip install --config-settings json=True --config-settings use-msgpackc=c++11 "%target%"
if errorlevel 1 goto failed
call :run "%pixi%" run -e py313 python -m pip check
if errorlevel 1 goto failed
call :run "%pixi%" run -e py313 python -c "import pymol2; from pymol.Qt import QtWidgets; p = pymol2.PyMOL(); p.start(); p.cmd.fragment('gly'); assert p.cmd.count_atoms() > 0; p.stop()"
if errorlevel 1 goto failed
if "%dry_run%"=="1" (echo Preview only; nothing installed.) else echo Installed and checked: headless core and Qt imports.
echo Launch from any folder in PowerShell:
echo ^& "%pixi%" run --manifest-path "%root%pixi.toml" -e py313 pymolish
echo Or in cmd:
echo "%pixi%" run --manifest-path "%root%pixi.toml" -e py313 pymolish
popd
exit /b 0

:confirm
if "%yes%"=="1" exit /b 0
choice /c YN /n /m "%~1 [Y/N] "
if errorlevel 2 exit /b 1
if errorlevel 1 exit /b 0
exit /b 1
:run
echo + %*
if "%dry_run%"=="1" exit /b 0
%*
exit /b %errorlevel%
:failed
set "result=%errorlevel%"
if "%result%"=="0" set "result=1"
echo Installation stopped. Resolve the message above, then rerun install.cmd.
popd
exit /b %result%
:help
echo Usage: install.cmd [--dry-run] [--yes] [--extras "chem,fix,ai"]
echo Core only: --extras "" ; --yes accepts required setup, not optional extras.
exit /b 0
