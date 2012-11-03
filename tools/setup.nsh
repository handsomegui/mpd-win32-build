!include MUI2.nsh

##### Commonly used strings
!define GraphicsDir "${NSISDIR}\Contrib\Graphics"
!define UninstKey   "Software\Microsoft\Windows\CurrentVersion\Uninstall\${AppName}"
!define UninstFile  "uninst-${AppId}.exe"

##### Compiler configuration
OutFile       "${AppId}-${AppVersion}-setup.exe"
SetCompressor /SOLID lzma

##### General options
Name       "${AppName}"
InstallDir "$PROGRAMFILES\${AppName}"

##### Manifest options
XPStyle               on
RequestExecutionLevel admin

##### UI options
!define MUI_ICON                     "${GraphicsDir}\Icons\orange-install.ico"
!define MUI_UNICON                   "${GraphicsDir}\Icons\orange-uninstall.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP       "${GraphicsDir}\Header\orange.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "${GraphicsDir}\Wizard\orange.bmp"
!define MUI_ABORTWARNING

##### Installer pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

##### Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

##### Language settings
!insertmacro MUI_LANGUAGE "English"

###### Installation
Section
    !insertmacro INSTALL_FILES
    WriteRegStr   HKLM ${UninstKey} "DisplayName"       "${AppName}"
    WriteRegStr   HKLM ${UninstKey} "DisplayAppVersion" "${AppVersion}"
    WriteRegStr   HKLM ${UninstKey} "UninstallString"   '"$INSTDIR\${UninstFile}"'
    WriteRegDWORD HKLM ${UninstKey} "NoModify" 1
    WriteRegDWORD HKLM ${UninstKey} "NoRepair" 1
    WriteUninstaller "$INSTDIR\${UninstFile}"
SectionEnd

###### Uninstallation
Section "Uninstall"
    !insertmacro UNINSTALL_FILES
    DeleteRegKey HKLM ${UninstKey}
    Delete "$INSTDIR\${UninstFile}"
    RMDir "$INSTDIR"
SectionEnd
