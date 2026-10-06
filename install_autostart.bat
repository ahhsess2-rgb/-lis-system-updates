@echo off
rem Run once (double-click). Creates: auto-start with Windows + desktop shortcut.
cd /d "%~dp0"

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut($env:APPDATA+'\Microsoft\Windows\Start Menu\Programs\Startup\LIS Server.lnk'); $s.TargetPath='wscript.exe'; $s.Arguments='\"%~dp0lis_server_hidden.vbs\"'; $s.WorkingDirectory='%~dp0'; $s.WindowStyle=7; $s.Save(); $d=$w.CreateShortcut([Environment]::GetFolderPath('Desktop')+'\Specialized Hematologist Lab.lnk'); $d.TargetPath='%~dp0open_lab.bat'; $d.WorkingDirectory='%~dp0'; $d.IconLocation='%~dp0static\icon\lab-icon.ico'; $d.WindowStyle=7; $d.Save()"

if errorlevel 1 (
    echo Failed to create the shortcuts. Send a screenshot of the message above.
    pause
    exit /b 1
)

rem Start the server now without waiting for a reboot
start "" wscript.exe "%~dp0lis_server_hidden.vbs"

echo.
echo Done:
echo  - The server now starts automatically with Windows (no window).
echo  - Desktop shortcut "Specialized Hematologist Lab": one click opens the program.
echo.
pause
