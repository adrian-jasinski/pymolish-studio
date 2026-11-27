# Run after PyInstaller, from any directory. No Python is needed by Setup.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$bundle = Join-Path $root 'dist\pymolish'
$output = Join-Path $root 'dist'
$build = Join-Path $root 'build\windows-installer'
$version = [regex]::Match(
    (Get-Content (Join-Path $root 'layer0\Version.h') -Raw),
    '(?m)^#define _PyMOL_VERSION "(\d+\.\d+\.\d+)"'
).Groups[1].Value
if (!$version) { throw 'Cannot read the version from layer0/Version.h' }
$exe = Get-Item (Join-Path $bundle 'pymolish.exe')
if ($exe.VersionInfo.ProductVersion -ne $version) {
    throw "Bundle version differs from $version; rebuild packaging/pyinstaller.spec first."
}
if (!(Test-Path (Join-Path $bundle '_internal\pymol\pymol_path\LICENSE'))) {
    throw 'Incomplete bundle: missing application resources/notices.'
}

# The official compiler is a build tool only; verify before executing it.
$innoVersion = '6.7.1'
$sha256 = '4d11e8050b6185e0d49bd9e8cc661a7a59f44959a621d31d11033124c4e8a7b0'
New-Item -ItemType Directory -Force $build | Out-Null
$download = Join-Path $build "innosetup-$innoVersion.exe"
$compilerDir = Join-Path $build "InnoSetup-$innoVersion"
Invoke-WebRequest "https://github.com/jrsoftware/issrc/releases/download/is-6_7_1/innosetup-$innoVersion.exe" -OutFile $download
if ((Get-FileHash $download -Algorithm SHA256).Hash -ne $sha256) {
    throw 'Inno Setup download failed SHA-256 verification.'
}
$process = Start-Process -FilePath $download -Wait -PassThru -ArgumentList @(
    '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/SP-', '/CURRENTUSER',
    '/NOICONS', '/MERGETASKS="!fileassoc"', "/DIR=`"$compilerDir`""
)
if ($process.ExitCode -ne 0) { throw "Inno Setup installation failed: $($process.ExitCode)" }
$compiler = Join-Path $compilerDir 'ISCC.exe'

# Only these installer-owned relative paths may be pruned by a later upgrade.
$manifest = Join-Path $build 'payload-files.txt'
$paths = Get-ChildItem $bundle -File -Recurse | ForEach-Object {
    $_.FullName.Substring($bundle.Length + 1)
}
[System.IO.File]::WriteAllLines($manifest, [string[]]($paths | Sort-Object), [System.Text.UTF8Encoding]::new($true))
$installer = Join-Path $output "pymolish-$version-Windows-X64-setup.exe"
& $compiler "/DAppVersion=$version" "/DBundleDir=$bundle" "/DOutputDir=$output" "/DPayloadManifest=$manifest" (Join-Path $PSScriptRoot 'windows.iss')
if ($LASTEXITCODE -ne 0) { throw "Installer compilation failed: $LASTEXITCODE" }
if (!(Test-Path $installer)) { throw "Installer was not produced: $installer" }
Get-FileHash $installer -Algorithm SHA256
