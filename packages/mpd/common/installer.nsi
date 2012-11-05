!define APP_NAME "Music Player Daemon"

!include standard.nsh

!define SHORTCUT_DIR       "$SMPROGRAMS\${APP_NAME}"
!define SHORTCUT_EXE       "${SHORTCUT_DIR}\${APP_NAME}.lnk"
!define SHORTCUT_EDIT_CONF "${SHORTCUT_DIR}\Edit mpd.conf.lnk"

!define NOTEPAD   "$WINDIR\system32\notepad.exe"
!define CONFIGURE "$PLUGINSDIR\mpd-configure.cmd"
!define MPD_EXE   "$INSTDIR\bin\mpd.exe"
!define MPD_CONF  "$INSTDIR\profile\mpd.conf"

Var MusicDir

!insertmacro MUI_PAGE_DIRECTORY

!define MUI_PAGE_HEADER_TEXT                "Choose music folder"
!define MUI_PAGE_HEADER_SUBTEXT             "Choose folder where your music files reside."
!define MUI_DIRECTORYPAGE_TEXT_TOP          "The following folder would be used by ${APP_NAME} for music files. To choose different folder, click Browse and select another folder."
!define MUI_DIRECTORYPAGE_TEXT_DESTINATION  "Music Folder"
!define MUI_DIRECTORYPAGE_VARIABLE          $MusicDir
!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Function .onInit
    InitPluginsDir
    File /oname=${CONFIGURE} "common\mpd-configure.cmd"
    StrCpy $MusicDir $MUSIC
FunctionEnd

Section
    !insertmacro INSTALL_FILES

    DetailPrint "Generating configuration file..."
    SetDetailsPrint none
    nsExec::Exec '"${CONFIGURE}" "$INSTDIR\profile" "$MusicDir"'
    Pop $0
    SetDetailsPrint both

    CreateDirectory "${SHORTCUT_DIR}"
    CreateShortCut  "${SHORTCUT_EXE}"       '"${MPD_EXE}"' '"${MPD_CONF}"'
    CreateShortCut  "${SHORTCUT_EDIT_CONF}" '"${NOTEPAD}"' '"${MPD_CONF}"'

    !insertmacro CREATE_UNINSTALLER
SectionEnd

Section "Uninstall"
    Delete "${SHORTCUT_EXE}"
    Delete "${SHORTCUT_EDIT_CONF}"
    RMDir  "${SHORTCUT_DIR}"
    !insertmacro UNINSTALL
SectionEnd
