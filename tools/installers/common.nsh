Name          "${APP_NAME}"
SetCompressor /SOLID lzma

!define MULTIUSER_EXECUTIONLEVEL                         Highest
!define MULTIUSER_INSTALLMODE_INSTDIR                    "${APP_NAME}"
!define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_KEY       "Software\${APP_NAME}"
!define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_VALUENAME "InstallDir"
!define MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_KEY       "Software\${APP_NAME}"
!define MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_VALUENAME "InstallMode"
!define MULTIUSER_INSTALLMODE_COMMANDLINE
!define MULTIUSER_MUI

!include LogicLib.nsh
!include MultiUser.nsh
!include MUI2.nsh

!define GFX_DIR     "${NSISDIR}\Contrib\Graphics"
!define UNINST_KEY  "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
!define UNINST_FILE "$INSTDIR\uninstall.exe"

!define MUI_ICON                     "${GFX_DIR}\Icons\orange-install.ico"
!define MUI_UNICON                   "${GFX_DIR}\Icons\orange-uninstall.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP       "${GFX_DIR}\Header\orange.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "${GFX_DIR}\Wizard\orange.bmp"
!define MUI_ABORTWARNING

!macro REGISTER_UNINSTALLER ROOT
    WriteRegStr   ${ROOT} "${UNINST_KEY}" "DisplayName"       "${APP_NAME}"
    WriteRegStr   ${ROOT} "${UNINST_KEY}" "DisplayAppVersion" "${APP_VERSION}"
    WriteRegStr   ${ROOT} "${UNINST_KEY}" "UninstallString"   "${UNINST_FILE}"
    WriteRegDWORD ${ROOT} "${UNINST_KEY}" "NoModify" 1
    WriteRegDWORD ${ROOT} "${UNINST_KEY}" "NoRepair" 1
!macroend

!macro CREATE_UNINSTALLER
    WriteUninstaller "${UNINST_FILE}"
    ${If} $MultiUser.InstallMode == "AllUsers"
        !insertmacro REGISTER_UNINSTALLER HKLM
    ${Else}
        !insertmacro REGISTER_UNINSTALLER HKCU
    ${EndIf}
!macroend

!macro UNINSTALL
    ${If} $MultiUser.InstallMode == "AllUsers"
        DeleteRegKey HKLM "${UNINST_KEY}"
    ${Else}
        DeleteRegKey HKCU "${UNINST_KEY}"
    ${EndIf}
    RMDir  /r "$INSTDIR\bin"
    RMDir  /r "$INSTDIR\doc"
    Delete "${UNINST_FILE}"
    RMDir  "$INSTDIR"
!macroend
