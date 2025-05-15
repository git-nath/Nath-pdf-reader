@echo off
REM Create a virtual environment
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt
pip install pyinstaller

REM Create the executable
pyinstaller ^
    --name=NathFileReader ^
    --onefile ^
    --windowed ^
    --icon=assets/icon.ico ^
    --add-data "assets;assets" ^
    --add-data "README.md;." ^
    main.py

echo Build complete! The executable is in the 'dist' folder.
pause
