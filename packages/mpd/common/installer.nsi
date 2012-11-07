!define APP_NAME "Music Player Daemon"

!include common.nsh

!define APP         "$INSTDIR\bin\mpd.exe"
!define NOTEPAD     "$SYSDIR\notepad.exe"
!define SC_TOOL     "$SYSDIR\sc.exe"
!define NET_TOOL    "$SYSDIR\net.exe"
!define GENCONFIG   "$PLUGINSDIR\genconfig.cmd"
!define CONFIG_FILE "$ConfigDir\mpd.conf"
!define SVC_NAME    "MusicPlayerDaemon"

!define SHORTCUT_DIR       "$SMPROGRAMS\${APP_NAME}"
!define SHORTCUT_APP       "${SHORTCUT_DIR}\${APP_NAME}.lnk"
!define SHORTCUT_START     "${SHORTCUT_DIR}\Start MPD.lnk"
!define SHORTCUT_STOP      "${SHORTCUT_DIR}\Stop MPD.lnk"
!define SHORTCUT_EDIT_CONF "${SHORTCUT_DIR}\Edit mpd.conf.lnk"

Var MusicDir
Var ConfigDir
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
    
    ${If} $MultiUser.InstallMode == "AllUsers"
        StrCpy $ConfigDir "$APPDATA\mpd"
    ${Else}
        StrCpy $ConfigDir "$LOCALAPPDATA\mpd"
    ${EndIf}
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

!macro EXEC MSG CMD
      DetailPrint `${MSG}`
      SetDetailsPrint none
      nsExec::Exec `${CMD}`
      Pop $0
      SetDetailsPrint both
!macroend

Section
    !insertmacro INSTALL_FILES

    ${If} $HasConfig == "n"
        !insertmacro EXEC "Generating configuration file" \
            '"${GENCONFIG}" "$ConfigDir" "$MusicDir"'
    ${EndIf}
    
    ${If} $MultiUser.InstallMode == "AllUsers"
        !insertmacro EXEC "Registering service" \
            '"${SC_TOOL}" create ${SVC_NAME} binpath= "${APP}" displayname= "${APP_NAME}" obj= "NT AUTHORITY\LocalService" start= delayed-auto depend= "AudioSrv"'
        !insertmacro EXEC "Starting service" \
            '"${NET_TOOL}" start ${SVC_NAME}'
    ${EndIf}

    CreateDirectory "${SHORTCUT_DIR}"

    ${If} $MultiUser.InstallMode == "AllUsers"
        CreateShortCut "${SHORTCUT_START}" '"${NET_TOOL}"' 'start ${SVC_NAME}'
        CreateShortCut "${SHORTCUT_STOP}"  '"${NET_TOOL}"' 'stop  ${SVC_NAME}'
    ${Else}
        CreateShortCut "${SHORTCUT_APP}" '"${APP}"'
    ${EndIf}

    CreateShortCut "${SHORTCUT_EDIT_CONF}" '"${NOTEPAD}"' '"${CONFIG_FILE}"'

    !insertmacro CREATE_UNINSTALLER
SectionEnd

Section "Uninstall"
    ${If} $MultiUser.InstallMode == "AllUsers"
        !insertmacro EXEC "Stopping service" \
            '"${NET_TOOL}" stop ${SVC_NAME}'
        !insertmacro EXEC "Unregistering service" \
            '"${SC_TOOL}" delete ${SVC_NAME}'
    ${EndIf}

    Delete "${SHORTCUT_EDIT_CONF}"
    ${If} $MultiUser.InstallMode == "AllUsers"
        Delete "${SHORTCUT_START}"
        Delete "${SHORTCUT_STOP}"
    ${Else}
        Delete "${SHORTCUT_APP}"
    ${EndIf}
    RMDir "${SHORTCUT_DIR}"

    !insertmacro UNINSTALL
SectionEnd
