# NathFile Reader

A modern file reader application for Windows 11 that supports PDF, DOCX, and PPTX files.

## Features
- View PDF, DOCX, and PPTX files
- Search within documents
- Bookmark pages
- Print documents
- Modern Windows 11 UI
- File associations for supported formats
- Light and dark theme support

## Installation

### Method 1: Using the Installer (Recommended)
1. Download the latest installer (`NathFileReader-Setup.exe`) from the releases
2. Run the installer and follow the on-screen instructions
3. Launch NathFile Reader from the Start Menu

### Method 2: Portable Version
1. Download the portable zip file (`NathFileReader-Portable.zip`)
2. Extract the zip file to your preferred location
3. Run `NathFileReader.exe` from the extracted folder

### Method 3: From Source
1. Install Python 3.7 or higher
2. Clone this repository
3. Run `pip install -r requirements.txt`
4. Run `python main.py`

## Building from Source

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. Build the executable:
   ```
   .\build.bat
   ```

3. Create the installer (requires Inno Setup):
   - Install Inno Setup from https://jrsoftware.org/isdl.php
   - Right-click on `setup.iss` and select "Compile"
   - The installer will be created in the `installer` folder

## Usage

- Open files using the File > Open menu or by double-clicking associated file types
- Use the search function (Ctrl+F) to find text within documents
- Add bookmarks to quickly navigate to important pages
- Print documents using the Print option in the File menu

## License

MIT License - Free for personal and commercial use
