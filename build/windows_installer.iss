[Setup]
AppName=easysnec
AppVersion={#VersionNo}


; DefaultDirName=easysnec
DefaultDirName={autopf}\easysnec
DefaultGroupName=easysnec
OutputBaseFilename=install_easysnec_{#VersionNo}
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
[Files]
Source: "..\dist\binary\easysnec-{#VersionNo}.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\src\easysnec\qml\*.*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
; [Icons]
; Name: "{group}\MyApp"; Filename: "{app}\MyApp.exe"
; Name: "{commondesktop}\MyApp"; Filename: "{app}\MyApp.exe"; Tasks: desktopicon
; [Tasks]
; Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons"; Flags: unchecked