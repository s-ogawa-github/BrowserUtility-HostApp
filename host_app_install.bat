REG ADD "HKCU\Software\Google\Chrome\NativeMessagingHosts\browser_utility_host_app" /ve /t REG_SZ /d "%~dp0chrome\browser_utility_host_app.json" /f
REG ADD "HKCU\Software\Mozilla\NativeMessagingHosts\browser_utility_host_app" /ve /t REG_SZ /d "%~dp0firefox\browser_utility_host_app.json" /f

@echo off

set chrome_json_path=%~dp0chrome\browser_utility_host_app.json
set firefox_json_path=%~dp0firefox\browser_utility_host_app.json
set bat_path=%~dp0src\browser_utility_host_app.bat
set bat_path=%bat_path:\=\\%

call :make_json %chrome_json_path%
call :make_json %firefox_json_path%

echo;
echo browser_utility_host_app.json for chrome created
type %chrome_json_path%

echo;
echo browser_utility_host_app.json for firefox created
type %firefox_json_path%

pause
exit /b

:make_json
set json=%1
move /y %json% %json%_temp
setlocal enabledelayedexpansion
for /f "delims=" %%A in (!json!_temp) do (
    set line=%%A
    echo "!line!" | find "path" >NUL
    if not ERRORLEVEL 1 (
        echo   "path": "%bat_path%",>>"!json!"
    ) else (
        echo !line!>>"!json!"
    )
)
endlocal
del %json%_temp
exit /b