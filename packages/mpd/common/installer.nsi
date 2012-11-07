!define APP_NAME "Music Player Daemon"

!include common.nsh

!define APP       "$INSTDIR\bin\mpd.exe"
!define NOTEPAD   "$WINDIR\system32\notepad.exe"
!define GENCONFIG "$PLUGINSDIR\genconfig.cmd"

!define CONFIG_DIR  "$LOCALAPPDATA\mpd"
!define CONFIG_FILE "${CONFIG_DIR}\mpd.conf"

!define SHORTCUT_DIR       "$SMPROGRAMS\${APP_NAME}"
!define SHORTCUT_APP       "${SHORTCUT_DIR}\${APP_NAME}.lnk"
!define SHORTCUT_EDIT_CONF "${SHORTCUT_DIR}\Edit mpd.conf.lnk"

Var MusicDir
Var HasConfig

!insertmacro MULTIUSER_PAGE_INSTALLMODE
!insertmacro MUI_PAGE_DIRECTORY
!define MUI_PAGE_CUSTOMFUNCTION_PRE        MusicDirPre
!define MUI_PAGE_HEADER_TEXT               "Choose music folder"
!define MUI_PAGE_HEADER_SUBTEXT            "Choose folder where your music files reside."
!define MUI_DIRECTORYPAGE_TEXT_TOP         "The following folder would be used by ${APP_NAME} for music files. To choose different folder, click Browse and select another folder."
!define MUI_DIRECTORYPAGE_TEXT_DESTINATION "Music Folder"
!define MUI_DIRECTORYPAGE_VARIABLE         $MusicDir
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Function .onInit
    !insertmacro MULTIUSER_INIT
    InitPluginsDir
    File /oname=${GENCONFIG} "common\genconfig.cmd"
    StrCpy $MusicDir $MUSIC
FunctionEnd

Function un.onInit
    !insertmacro MULTIUSER_UNINIT
FunctionEnd

Function MusicDirPre
    ${If} ${FileExists} "${CONFIG_FILE}"
        StrCpy $HasConfig "y"
        Abort
    ${Else}
        StrCpy $HasConfig "n"
    ${EndIf}
FunctionEnd

Section
    !insertmacro INSTALL_FILES

    ${If} $HasConfig == "n"
      DetailPrint "Generating configuration file..."
      SetDetailsPrint none
      nsExec::Exec '"${GENCONFIG}" "${CONFIG_DIR}" "$MusicDir"'
      Pop $0
      SetDetailsPrint both
    ${EndIf}

    CreateDirectory "${SHORTCUT_DIR}"
    CreateShortCut  "${SHORTCUT_APP}"       '"${APP}"'
    CreateShortCut  "${SHORTCUT_EDIT_CONF}" '"${NOTEPAD}"' '"${CONFIG_FILE}"'

    !insertmacro CREATE_UNINSTALLER
SectionEnd

Section "Uninstall"
    Delete "${SHORTCUT_APP}"
    Delete "${SHORTCUT_EDIT_CONF}"
    RMDir  "${SHORTCUT_DIR}"
    !insertmacro UNINSTALL
SectionEnd
