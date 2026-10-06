@echo off
rem Opens the LIS window. Starts the hidden server if needed and waits for it (up to 90 sec).
cd /d "%~dp0"
set PORT=9090

netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul
if errorlevel 1 (
    echo Starting the LIS server, please wait...
    start "" wscript.exe "%~dp0lis_server_hidden.vbs"
)

set /a N=0
:wait
netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul
if not errorlevel 1 goto ready
set /a N+=1
if %N% GEQ 90 goto fail
echo Waiting for server... %N% / 90
ping -n 2 127.0.0.1 >nul
goto wait

:fail
echo.
echo Server did not start. Open server_log.txt in this folder and send the last lines.
pause
exit /b 1

:ready
set "EDGE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if exist "%EDGE%" goto edge
set "EDGE=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
if exist "%EDGE%" goto edge
start "" "http://127.0.0.1:%PORT%"
exit /b 0

:edge
start "" "%EDGE%" --app=http://127.0.0.1:%PORT%
exit /b 0
