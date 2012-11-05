!define APP_NAME "Music Player Command"

!include standard.nsh

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section
    !insertmacro INSTALL_FILES
    !insertmacro CREATE_UNINSTALLER
SectionEnd

Section "Uninstall"
    !insertmacro UNINSTALL
SectionEnd
