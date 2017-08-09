SET src=%1
rem set dst=%~dp0%src:~0,-3%js%
set dst=%src:~0,-4%js%

echo %dst%

"C:\Program Files\nodejs\node.exe" "D:/Program Files/RapydScript-master/bin/rapydscript" -V

pause