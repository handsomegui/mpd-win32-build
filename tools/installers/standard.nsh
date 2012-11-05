!ifndef OLDISH_UI
    !include MUI2.nsh
!endif

!define GFX_DIR     "${NSISDIR}\Contrib\Graphics"
!define UNINST_KEY  "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
!define UNINST_FILE "uninstall.exe"

Name                  "${APP_NAME}"
InstallDir            "$LOCALAPPDATA\${APP_NAME}"
SetCompressor         /SOLID lzma
XPStyle               on
RequestExecutionLevel user

!ifdef OLDISH_UI
    InstallColors /windows
    Icon          "${GFX_DIR}\Icons\orange-install.ico"
    UninstallIcon "${GFX_DIR}\Icons\orange-uninstall.ico"
  
    Page directory
    Page instfiles

    UninstPage uninstConfirm
    UninstPage instfiles
!else
    !define MUI_ICON                     "${GFX_DIR}\Icons\orange-install.ico"
    !define MUI_UNICON                   "${GFX_DIR}\Icons\orange-uninstall.ico"
    !define MUI_HEADERIMAGE
    !define MUI_HEADERIMAGE_BITMAP       "${GFX_DIR}\Header\orange.bmp"
    !define MUI_WELCOMEFINISHPAGE_BITMAP "${GFX_DIR}\Wizard\orange.bmp"
    !define MUI_ABORTWARNING

    !insertmacro MUI_PAGE_WELCOME
    !insertmacro MUI_PAGE_DIRECTORY
    !insertmacro MUI_PAGE_INSTFILES
  
    !insertmacro MUI_UNPAGE_CONFIRM
    !insertmacro MUI_UNPAGE_INSTFILES

    !insertmacro MUI_LANGUAGE "English"
!endif

!macro CREATE_UNINSTALLER
    WriteUninstaller "$INSTDIR\${UNINST_FILE}"
    WriteRegStr   HKCU "${UNINST_KEY}" "DisplayName"       "${APP_NAME}"
    WriteRegStr   HKCU "${UNINST_KEY}" "DisplayAppVersion" "${APP_VERSION}"
    WriteRegStr   HKCU "${UNINST_KEY}" "UninstallString"   "$INSTDIR\${UNINST_FILE}"
    WriteRegDWORD HKCU "${UNINST_KEY}" "NoModify" 1
    WriteRegDWORD HKCU "${UNINST_KEY}" "NoRepair" 1
!macroend

!macro UNINSTALL_ALL
    DeleteRegKey HKCU "${UNINST_KEY}"
    RMDir  /r "$INSTDIR\bin"
    RMDir  /r "$INSTDIR\doc"
    Delete "$INSTDIR\${UNINST_FILE}"
    RMDir  "$INSTDIR"
!macroend
