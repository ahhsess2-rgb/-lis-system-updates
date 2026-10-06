@echo off
rem LIS server guard: runs app.py and restarts it if it stops. ASCII-only, CRLF line endings.
cd /d "%~dp0"
set PORT=9090
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

set "PY="
if exist "venv\Scripts\python.exe" set "PY=venv\Scripts\python.exe"
if not defined PY if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
if not defined PY (where python >nul 2>nul && set "PY=python")
if not defined PY set "PY=py -3"

:loop
netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul
if not errorlevel 1 (
    ping -n 11 127.0.0.1 >nul
    goto loop
)
if exist server_log.txt for %%F in (server_log.txt) do if %%~zF GTR 5000000 move /y server_log.txt server_log.old.txt >nul
echo [%date% %time%] starting server using %PY% >> server_log.txt
%PY% app.py >> server_log.txt 2>&1
echo [%date% %time%] server stopped, restarting >> server_log.txt
ping -n 4 127.0.0.1 >nul
goto loop
