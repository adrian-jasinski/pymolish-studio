; Compile through build_windows_installer.ps1; all paths/version come from it.
#ifndef AppVersion
  #error AppVersion must come from layer0/Version.h
#endif

[Setup]
AppId=pymolish-studio
AppName=pymolish-studio
AppVersion={#AppVersion}
AppPublisher=pymolish-studio contributors
AppPublisherURL=https://github.com/adrian-jasinski/pymolish-studio
VersionInfoVersion={#AppVersion}
VersionInfoDescription=pymolish-studio Setup
DefaultDirName={localappdata}\Programs\pymolish-studio
PrivilegesRequired=lowest
ArchitecturesAllowed=x64os
ArchitecturesInstallIn64BitMode=x64os
MinVersion=10.0
WizardStyle=modern
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\pymolish.exe
OutputDir={#OutputDir}
OutputBaseFilename=pymolish-{#AppVersion}-Windows-X64-setup
Compression=lzma2
SolidCompression=yes
SetupMutex=pymolish-studio-setup
CloseApplications=yes
CloseApplicationsFilter=*.exe,*.dll,*.pyd
RestartApplications=no

[Files]
Source: "{#BundleDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#PayloadManifest}"; DestDir: "{app}"; DestName: ".pymolish-files"; Flags: ignoreversion

[Icons]
Name: "{userprograms}\pymolish-studio"; Filename: "{app}\pymolish.exe"; WorkingDir: "{userdocs}"

[Run]
Filename: "{app}\pymolish.exe"; WorkingDir: "{userdocs}"; Description: "Launch pymolish-studio"; Flags: nowait postinstall skipifsilent

[Code]
function PayloadPath(const Name: String): Boolean;
begin
  { A modified manifest must never delete outside the application folder. }
  Result := (Name <> '') and (Copy(Name, 1, 1) <> '\') and
    (Copy(Name, 1, 1) <> '/') and (Pos(':', Name) = 0) and
    (Pos('/', Name) = 0) and (Pos('..', Name) = 0) and
    (CompareText(Name, '.pymolish-files') <> 0) and
    (CompareText(Copy(Name, 1, 5), 'unins') <> 0);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Previous, Current: TStringList;
  I: Integer;
  Name, Path, AppDir: String;
begin
  if CurStep <> ssInstall then
    Exit;
  AppDir := ExpandConstant('{app}');
  if not FileExists(AppDir + '\.pymolish-files') then
    Exit;
  ExtractTemporaryFile('.pymolish-files');
  Previous := TStringList.Create;
  Current := TStringList.Create;
  try
    Previous.LoadFromFile(AppDir + '\.pymolish-files');
    Current.LoadFromFile(ExpandConstant('{tmp}\.pymolish-files'));
    for I := 0 to Previous.Count - 1 do begin
      Name := Previous[I];
      if PayloadPath(Name) and (Current.IndexOf(Name) < 0) then begin
        Path := AppDir + '\' + Name;
        if FileExists(Path) and not DeleteFile(Path) then
          RaiseException('Cannot remove an obsolete application file. Close pymolish and retry: ' + Path);
        Path := ExtractFileDir(Path);
        while (CompareText(Path, AppDir) <> 0) and RemoveDir(Path) do
          Path := ExtractFileDir(Path);
      end;
    end;
  finally
    Previous.Free;
    Current.Free;
  end;
end;
