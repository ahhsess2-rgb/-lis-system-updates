@echo off
rem Removes auto-start and stops the server
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\LIS Server.lnk" 2>nul
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":9090 .*LISTENING"') do taskkill /F /PID %%p >nul 2>nul
taskkill /F /FI "WINDOWTITLE eq LIS Server*" >nul 2>nul
echo Auto-start removed and server stopped.
pause
