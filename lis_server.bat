@echo off
chcp 65001 >nul
rem حارس السيرفر: يشغّل البرنامج ويعيد تشغيله تلقائيًا لو وقع. لا يحتاج أي تدخل.
cd /d "%~dp0"
set PORT=9090

set "PY="
if exist "venv\Scripts\python.exe" set "PY=venv\Scripts\python.exe"
if not defined PY if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
if not defined PY (where python >nul 2>nul && set "PY=python")
if not defined PY set "PY=py -3"

:loop
rem لو السيرفر شغّال أصلاً (مثلاً بعد تحديث تلقائي) ننتظر ولا نشغّل نسخة ثانية
netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul
if not errorlevel 1 (
    ping -n 11 127.0.0.1 >nul
    goto loop
)
rem تدوير السجل: لو كبر عن ~5MB ننقله لنسخة قديمة حتى ما يمتلئ القرص
if exist server_log.txt for %%F in (server_log.txt) do if %%~zF GTR 5000000 move /y server_log.txt server_log.old.txt >nul
echo [%date% %time%] starting server >> server_log.txt
%PY% app.py >> server_log.txt 2>&1
echo [%date% %time%] server stopped, restarting >> server_log.txt
ping -n 4 127.0.0.1 >nul
goto loop
