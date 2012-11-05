!define APP_NAME "Music Player Daemon"

!include standard.nsh

!define SHORTCUT_DIR       "$SMPROGRAMS\${APP_NAME}"
!define SHORTCUT_EXE       "${SHORTCUT_DIR}\${APP_NAME}.lnk"
!define SHORTCUT_EDIT_CONF "${SHORTCUT_DIR}\Edit mpd.conf.lnk"

!define CONFIGURE "$PLUGINSDIR\mpd-configure.cmd"
!define MPD_EXE   "$INSTDIR\bin\mpd.exe"
!define MPD_CONF  "$INSTDIR\conf\mpd.conf"

!macro INSTALL_SHORTCUTS
    CreateDirectory "${SHORTCUT_DIR}"
    CreateShortCut  "${SHORTCUT_EXE}" \
        '"${MPD_EXE}"' \
        '"${MPD_CONF}"'
    CreateShortCut  "${SHORTCUT_EDIT_CONF}" \
        '"$WINDIR\system32\notepad.exe"' \
        '"${MPD_CONF}"'
!macroend

!macro UNINSTALL_SHORTCUTS
    Delete "${SHORTCUT_EXE}"
    Delete "${SHORTCUT_EDIT_CONF}"
    RMDir  "${SHORTCUT_DIR}"
!macroend

!macro GENERATE_CONFIG
    DetailPrint "Generating configuration file..."
    SetDetailsPrint none
    nsExec::Exec '"${CONFIGURE}" "$INSTDIR" "$MUSIC"'
    Pop $0
    SetDetailsPrint both
!macroend

Function .onInit
    InitPluginsDir
    File /oname=${CONFIGURE} "common\mpd-configure.cmd"
FunctionEnd

Section
    !insertmacro INSTALL_FILES
    !insertmacro GENERATE_CONFIG
    !insertmacro INSTALL_SHORTCUTS
    !insertmacro CREATE_UNINSTALLER
SectionEnd

Section "Uninstall"
    !insertmacro UNINSTALL_SHORTCUTS
    !insertmacro UNINSTALL_ALL
SectionEnd
