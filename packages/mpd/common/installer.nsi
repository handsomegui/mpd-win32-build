!define APP_NAME "Music Player Daemon"

!include standard.nsh

Section
    !insertmacro INSTALL_FILES
    !insertmacro CREATE_UNINSTALLER
SectionEnd

Section "Uninstall"
    !insertmacro UNINSTALL_ALL
SectionEnd