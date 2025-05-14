#define MyAppName "NathFile Reader"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "NathFile"
#define MyAppURL "https://nathfile.com"
#define MyAppExeName "NathFileReader.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-4765-8A7B-8C9D0E1F2A3B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=NathFileReader-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "associatepdf"; Description: "Associate PDF files"; GroupDescription: "File associations:"; Flags: unchecked
Name: "associatedocx"; Description: "Associate DOCX files"; GroupDescription: "File associations:"; Flags: unchecked
Name: "associatepptx"; Description: "Associate PPTX files"; GroupDescription: "File associations:"; Flags: unchecked

[Files]
Source: "dist\NathFileReader\*.*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCR; Subkey: ".pdf\OpenWithProgIds"; ValueType: string; ValueName: "NathFileReader.pdf"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associatepdf
Root: HKCR; Subkey: "NathFileReader.pdf"; ValueType: string; ValueName: ""; ValueData: "PDF Document"; Flags: uninsdeletekey; Tasks: associatepdf
Root: HKCR; Subkey: "NathFileReader.pdf\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\NathFileReader.exe,0"; Tasks: associatepdf
Root: HKCR; Subkey: "NathFileReader.pdf\shell\open\command"; ValueType: string; ValueName: ""; ValueData: "\"{app}\NathFileReader.exe\" \"%1\""; Tasks: associatepdf

Root: HKCR; Subkey: ".docx\OpenWithProgIds"; ValueType: string; ValueName: "NathFileReader.docx"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associatedocx
Root: HKCR; Subkey: "NathFileReader.docx"; ValueType: string; ValueName: ""; ValueData: "Word Document"; Flags: uninsdeletekey; Tasks: associatedocx
Root: HKCR; Subkey: "NathFileReader.docx\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\NathFileReader.exe,0"; Tasks: associatedocx
Root: HKCR; Subkey: "NathFileReader.docx\shell\open\command"; ValueType: string; ValueName: ""; ValueData: "\"{app}\NathFileReader.exe\" \"%1\""; Tasks: associatedocx

Root: HKCR; Subkey: ".pptx\OpenWithProgIds"; ValueType: string; ValueName: "NathFileReader.pptx"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associatepptx
Root: HKCR; Subkey: "NathFileReader.pptx"; ValueType: string; ValueName: ""; ValueData: "PowerPoint Presentation"; Flags: uninsdeletekey; Tasks: associatepptx
Root: HKCR; Subkey: "NathFileReader.pptx\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\NathFileReader.exe,0"; Tasks: associatepptx
Root: HKCR; Subkey: "NathFileReader.pptx\shell\open\command"; ValueType: string; ValueName: ""; ValueData: "\"{app}\NathFileReader.exe\" \"%1\""; Tasks: associatepptx
