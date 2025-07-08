# Creates a folder containing an executable version of the program with all unnecessary files removed
# Run with powershell.exe -noprofile -executionpolicy Bypass -file .\scripts/build.ps1
# If necessary, replace the beginning of the PyInstaller command with py, python3, or a specific interpreter path
#   If py or python3 causes an error, the automatic interpreter likely doesn't have PyInstaller installed
# Install new packages with pip --python C:/Users/vikto/AppData/Local/Programs/Python/Python310/python.exe install networkx (replace interpreter path if necessary)

if (Test-Path SE_exe) {
    rm SE_exe -force -Recurse
}
mkdir SE_exe
Copy-Item -Path $PWD\*  -Destination "SE_exe" -Recurse -Exclude @("*SE_exe", ".git", "__pycache__", ".gitignore", "__init__.py", "Instructions.docx", "README.txt", "scripts")
cd SE_exe
& py -m PyInstaller --onefile main.py --noconsole --icon=graphics/misc/SE.ico
Move-Item -Path dist/main.exe
rm main.spec -force
rmdir build -force -Recurse
rmdir sound_editing -force -Recurse
rm dist -force -Recurse
rm modules -force -Recurse
rm misc -force -Recurse
rm experiments -force -Recurse
rm artifacts -force -Recurse
rm -force main.py
rm -force configuration/dev_config.json
rm -force configuration/demographic_util.py
rm -force save_games/* -Recurse
rm -force .gitattributes
Remove-Item -Path notes\* -Exclude "Crash Log.txt"
Get-ChildItem -Path "graphics" -Filter "*.xcf" -Recurse | Remove-Item -Force
Get-ChildItem -Path "graphics" -Filter "*drawing*tools*" -Recurse | Remove-Item -Force -Recurse