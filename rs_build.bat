@SET src=%~1
@rem set dst=%~dp0%src:~0,-3%js%
@set dst=%src:~0,-3%js%
@rem @"C:\Program Files\nodejs\node.exe" "D:/Program Files/RapydScript-master/bin/rapydscript" %src% -6 -p -o  %dst%
"C:\Program Files\nodejs\node.exe" "D:/_dwork/_mypy/RapydScript_fix/bin/rapydscript" %src% -6 -p -o  %dst%
@rem "C:\Program Files\nodejs\node.exe" "D:/_dwork/_mypy/RapydScript_fix/bin/rapydscript" %src% -p -o  %dst%
@rem @"C:\Program Files\nodejs\node.exe" "D:/Program Files/RapydScript-master/bin/rapydscript" %src% -p -o  %dst%

