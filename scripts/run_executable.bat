@echo off

REM Change to SE_exe directory relative to this script
cd /d "%~dp0..\SE_exe"

REM Run the executable from within the SE_exe directory
start "" "main.exe"