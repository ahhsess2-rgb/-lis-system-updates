@echo off
chcp 65001 >nul
rem شغّله مرة وحدة فقط (دبل كليك). يسوي: تشغيل تلقائي مع الويندوز + اختصار على سطح المكتب.
cd /d "%~dp0"

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut($env:APPDATA+'\Microsoft\Windows\Start Menu\Programs\Startup\LIS Server.lnk'); $s.TargetPath='wscript.exe'; $s.Arguments='\"%~dp0lis_server_hidden.vbs\"'; $s.WorkingDirectory='%~dp0'; $s.WindowStyle=7; $s.Save(); $d=$w.CreateShortcut([Environment]::GetFolderPath('Desktop')+'\Specialized Hematologist Lab.lnk'); $d.TargetPath='%~dp0open_lab.bat'; $d.WorkingDirectory='%~dp0'; $d.IconLocation='%~dp0static\icon\lab-icon.ico'; $d.WindowStyle=7; $d.Save()"

if errorlevel 1 (
    echo فشل إنشاء الاختصارات. صوّر الرسالة أعلاه وأرسلها.
    pause
    exit /b 1
)

rem تشغيل السيرفر الآن بدون انتظار إعادة تشغيل الحاسبة
start "" wscript.exe "%~dp0lis_server_hidden.vbs"

echo.
echo تم بنجاح:
echo  - السيرفر يشتغل تلقائيًا مع كل تشغيل للويندوز (بدون نافذة).
echo  - اختصار "Specialized Hematologist Lab" على سطح المكتب: كليك واحد يفتح البرنامج.
echo.
pause
