' يشغّل lis_server.bat بدون أي نافذة ظاهرة
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = fso.GetParentFolderName(WScript.ScriptFullName)
sh.Run "cmd /c lis_server.bat", 0, False
