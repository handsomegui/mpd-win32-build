!define APP_NAME "Music Player Daemon"

!include standard.nsh

!define SHORTCUT_DIR           "$SMPROGRAMS\${APP_NAME}"
!define SHORTCUT_EDIT_MPD_CONF "${SHORTCUT_DIR}\Edit mpd.conf.lnk"

!define MPD_CONFIGURE "$PLUGINSDIR\mpd-configure.cmd"
!define MPD_CONF      "$INSTDIR\conf\mpd.conf"

!macro INSTALL_SHORTCUTS
    DetailPrint "Creating shortcuts..."
    CreateDirectory "${SHORTCUT_DIR}"
    CreateShortCut  "${SHORTCUT_EDIT_MPD_CONF}" \
        "$WINDIR\system32\notepad.exe" \
        '"${MPD_CONF}"'
!macroend

!macro UNINSTALL_SHORTCUTS
    Delete "${SHORTCUT_EDIT_MPD_CONF}"
    RMDir  "${SHORTCUR_DIR}"
!macroend

!macro GENERATE_CONFIG
    DetailPrint "Generating configuration file..."
    ExecWait    '"${MPD_CONFIGURE}" "$INSTDIR" "$MUSIC"'
!macroend

Function .onInit
    InitPluginsDir
    File /oname=${MPD_CONFIGURE} "common\mpd-configure.cmd"
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
