# Creates a folder containing an executable version of the program with all unnecessary files removed
# Run with powershell.exe -noprofile -executionpolicy Bypass -file .\scripts/build.ps1
# If necessary, replace the beginning of the PyInstaller command with py, python3, or a specific interpreter path
#   If py or python3 causes an error, the automatic interpreter likely doesn't have PyInstaller installed

if (Test-Path SFA_exe) {
    rm SFA_exe -force -Recurse
}
mkdir SFA_exe
Copy-Item -Path $PWD\*  -Destination "SFA_exe" -Recurse -Exclude @("*SFA_exe", ".git", "__pycache__", ".gitignore", "__init__.py", "Instructions.docx", "README.txt", "scripts")
cd SFA_exe
& C:/Users/vikto/AppData/Local/Programs/Python/Python310/python.exe -m PyInstaller --onefile Scramble_for_Africa.py --noconsole --icon=graphics/misc/SFA.ico
Move-Item -Path dist/Scramble_for_Africa.exe
rm Scramble_for_Africa.spec -force
rmdir build -force -Recurse
rm dist -force -Recurse
rm modules -force -Recurse
rm -force Scramble_for_Africa.py
rm -force configuration/dev_config.json
rm -force save_games/*.pickle
