# Creates a folder containing an executable version of the program with all unnecessary files removed
# Run with powershell.exe -noprofile -executionpolicy Bypass -file .\scripts/build.ps1
# If necessary, replace the beginning of the PyInstaller command with py, python3, or a specific interpreter path
#   If py or python3 causes an error, the automatic interpreter likely doesn't have PyInstaller installed

if (Test-Path SE_exe) {
    rm SE_exe -force -Recurse
}
mkdir SE_exe
Copy-Item -Path $PWD\*  -Destination "SE_exe" -Recurse -Exclude @("*SE_exe", ".git", "__pycache__", ".gitignore", "__init__.py", "Instructions.docx", "README.txt", "scripts")
cd SE_exe
& C:/Users/vikto/AppData/Local/Programs/Python/Python310/python.exe -m PyInstaller --onefile Second_Earth.py --noconsole --icon=graphics/misc/SE.ico
Move-Item -Path dist/Second_Earth.exe
rm Second_Earth.spec -force
rmdir build -force -Recurse
rm dist -force -Recurse
rm modules -force -Recurse
rm -force Second_Earth.py
rm -force configuration/dev_config.json
rm -force save_games/*.pickle
