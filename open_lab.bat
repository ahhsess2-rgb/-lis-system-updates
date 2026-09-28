@echo off
chcp 65001 >nul
rem هذا الملف يفتح نافذة البرنامج (اختصار سطح المكتب يشغّله). يتأكد أن السيرفر شغّال وينتظره إذا لسا يجهز.
cd /d "%~dp0"
set PORT=9090

netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul
if errorlevel 1 start "" wscript.exe "%~dp0lis_server_hidden.vbs"

set /a N=0
:wait
netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul
if not errorlevel 1 goto ready
set /a N+=1
if %N% GEQ 90 goto fail
ping -n 2 127.0.0.1 >nul
goto wait

:fail
echo السيرفر ما اشتغل. افتح server_log.txt بنفس المجلد وصوّر آخر سطور منه.
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
