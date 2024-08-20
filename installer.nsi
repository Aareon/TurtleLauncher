; Installer script for PySide6 Application

; Define your application name, version, and publisher
!define APPNAME "Turtle WoW Launcher"
!define APPVERSION "1.0.0"
!define PUBLISHER "Aareon Sullivan"

; Main install settings
Name "${APPNAME}"
InstallDir "$PROGRAMFILES\${APPNAME}"
OutFile "${APPNAME}-${APPVERSION}-setup.exe"

; Modern interface settings
!include "MUI2.nsh"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Set the installer icon (replace with your own icon if you have one)
;!define MUI_ICON ".\assets\images\icon.ico"

; Default section
Section "Install"

    ; Set output path to the installation directory
    SetOutPath $INSTDIR
    
    ; Add files to install
    File ".\__main__.dist\{APPNAME}.exe"
    ; Add any additional files or folders your application needs
    ; File /r ".\assets"

    ; Create start menu shortcut
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\${APPNAME}.exe"

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Add uninstall information to Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\Uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${APPVERSION}"

SectionEnd

; Uninstaller section
Section "Uninstall"
    
    ; Remove installed files
    Delete "$INSTDIR\executable.exe"
    ; Remove any additional files or folders you've added
    ; RMDir /r "$INSTDIR\assets"

    ; Remove start menu items
    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"

    ; Remove uninstaller
    Delete "$INSTDIR\Uninstall.exe"

    ; Remove installation directory
    RMDir "$INSTDIR"

    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"

SectionEnd