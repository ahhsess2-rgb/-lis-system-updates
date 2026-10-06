@echo off
cd /d "%~dp0"
set "OUT=%~dp0diagnose.txt"

echo === LIS diagnose %date% %time% > "%OUT%"
echo folder: %cd% >> "%OUT%"

echo. >> "%OUT%"
echo --- where python >> "%OUT%"
where python >> "%OUT%" 2>&1
echo --- where py >> "%OUT%"
where py >> "%OUT%" 2>&1
echo --- venv >> "%OUT%"
if exist "venv\Scripts\python.exe" (echo venv: yes >> "%OUT%") else (echo venv: no >> "%OUT%")
if exist ".venv\Scripts\python.exe" (echo .venv: yes >> "%OUT%") else (echo .venv: no >> "%OUT%")

echo. >> "%OUT%"
echo --- python version >> "%OUT%"
python --version >> "%OUT%" 2>&1

echo. >> "%OUT%"
echo --- required files >> "%OUT%"
for %%F in (app.py database.py translations.py daily_counter.py excel_export.py astm_host.py accounts_search.py license_manager.py auto_updater.py barcode_gen.py pdf_export.py local_config.py lis_server.bat lis_server_hidden.vbs) do call :chk %%F

echo. >> "%OUT%"
echo --- python packages and app.py syntax >> "%OUT%"
python -c "import importlib.util as u,sys; print('python', sys.version.split()[0], sys.executable); [print(('OK      ' if u.find_spec(m) else 'MISSING ')+m) for m in ('flask','werkzeug','markupsafe','openpyxl','docx','PIL','pdf_export','license_manager','auto_updater','barcode_gen')]; import ast; ast.parse(open('app.py',encoding='utf-8').read()); print('app.py syntax OK')" >> "%OUT%" 2>&1

echo. >> "%OUT%"
echo --- port 9090 >> "%OUT%"
netstat -ano | findstr ":9090" >> "%OUT%" 2>&1

echo. >> "%OUT%"
echo --- Windows Script Host enabled? (missing key = enabled) >> "%OUT%"
reg query "HKCU\Software\Microsoft\Windows Script Host\Settings" /v Enabled >> "%OUT%" 2>&1
reg query "HKLM\Software\Microsoft\Windows Script Host\Settings" /v Enabled >> "%OUT%" 2>&1

echo. >> "%OUT%"
echo --- last 30 lines of server_log.txt >> "%OUT%"
if exist server_log.txt (
  powershell -NoProfile -Command "Get-Content -Tail 30 -Encoding UTF8 server_log.txt" >> "%OUT%" 2>&1
) else (
  echo server_log.txt does not exist - the hidden server was never started >> "%OUT%"
)

echo.
echo DONE. Open diagnose.txt in this folder and send its content.
pause
exit /b 0

:chk
if exist "%~1" (echo OK      %~1 >> "%OUT%") else (echo MISSING %~1 >> "%OUT%")
exit /b 0
