@setlocal

@if "%~1"=="/force" (
    @shift
    set force=1
)

@if "%~1"=="" goto usage
@if "%~2"=="" goto usage

@set base_dir=%~f1
@set music_dir=%~f2
@set data_dir=%base_dir%\data
@set pls_dir=%data_dir%\playlists

@set f_music_dir=%music_dir:\=/%
@set f_data_dir=%data_dir:\=/%

@set conf_file=%base_dir%\mpd.conf
@set header=# Visit http://mpd.wikia.com/wiki/Configuration for more information.

@if exist "%conf_file%" (
    if not "%force%"=="1" goto :no_overwrite
)

@if not exist "%data_dir%\." @mkdir "%data_dir%"
@if not exist "%pls_dir%\."  @mkdir "%pls_dir%"

@echo %header%>"%conf_file%"
@call :write_line
@echo music_directory    "%f_music_dir%">>"%conf_file%"
@call :write_line
@echo playlist_directory "%f_data_dir%/playlists">>"%conf_file%"
@echo db_file            "%f_data_dir%/database">>"%conf_file%"
@echo log_file           "%f_data_dir%/log">>"%conf_file%"
@echo state_file         "%f_data_dir%/state">>"%conf_file%"
@echo sticker_file       "%f_data_dir%/stickers">>"%conf_file%"
@call :write_line
@echo bind_to_address    "localhost">>"%conf_file%"

@goto end

:write_line
@echo.>>"%conf_file%"
@goto end

:usage
@echo usage: %~n0 [/force] base_dir music_dir
@goto end

:no_overwrite
@echo mpd.conf already exists. Use /force to overwrite.
@goto end

:end
