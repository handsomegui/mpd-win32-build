!define APP_NAME "Music Player Command"

!include common.nsh

!insertmacro MULTIUSER_PAGE_INSTALLMODE
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Function .onInit
    !insertmacro MULTIUSER_INIT
FunctionEnd

Function un.onInit
    !insertmacro MULTIUSER_UNINIT
FunctionEnd

Section
    !insertmacro INSTALL_FILES
    !insertmacro CREATE_UNINSTALLER
SectionEnd

Section "Uninstall"
    !insertmacro UNINSTALL
SectionEnd
