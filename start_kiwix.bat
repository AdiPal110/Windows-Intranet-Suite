@echo off
cd /d "B:\Kiwix Windows\kiwix-tools_win-i686"
setlocal enabledelayedexpansion

:: Set the port number
set PORT=8088

:: Define the folder containing ZIM files
set ZIM_FOLDER=B:\Wiki

:: Build the list of ZIM files
set ZIM_FILES=
for %%F in ("%ZIM_FOLDER%\*.zim") do (
    set ZIM_FILES=!ZIM_FILES! "%%F"
)

:: Run Kiwix Server in a minimized separate window
start "" /min kiwix-serve.exe --port=%PORT% %ZIM_FILES%

:: Exit CMD
exit
