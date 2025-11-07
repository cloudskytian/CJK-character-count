@ECHO OFF
ECHO Start building...
pyinstaller main.spec
CD dist
REN "main" "CJK-character-count-vX.XX"
ECHO Build done!
ECHO Press Enter to exit.
PAUSE >nul
EXIT