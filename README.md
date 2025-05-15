# NathReader

A modern PDF reader application with a clean and intuitive interface, built with Python and CustomTkinter.

![NathReader Screenshot](screenshot.png)

## 📋 Features

- **Modern UI**: Clean, responsive interface with light and dark themes
- **PDF Support**: View and navigate PDF documents
- **Page Navigation**: Easily move between pages
- **Zoom Controls**: Zoom in/out and fit to width/page
- **Search**: Find text within documents
- **Bookmarks**: Save your place in documents
- **Recent Files**: Quick access to recently opened documents
- **Customizable**: Adjust appearance and behavior to your preferences

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Method 1: From PyPI (Coming Soon)
```bash
pip install nathreader
```

### Method 2: From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/nathreader.git
   cd nathreader
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🖥️ Usage

Run the application:
```bash
nathreader
```

Or to open a specific PDF:
```bash
nathreader path/to/your/document.pdf
```

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open document |
| `Ctrl+Q` | Quit |
| `Left/Right Arrow` | Previous/Next page |
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `F1` | Show help |

## 🛠️ Development

### Project Structure

```
nathreader/
├── src/
│   └── nathreader/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── core/
│       │   └── document.py
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── toolbar.py
│       │   ├── statusbar.py
│       │   ├── settings_dialog.py
│       │   └── theme.py
│       └── utils/
│           ├── __init__.py
│           ├── file_utils.py
│           └── settings.py
├── tests/
├── setup.py
├── requirements.txt
└── README.md
```

### Running Tests

```bash
pytest
```

### Building the Application

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name NathReader src/nathreader/__main__.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🏗️ Project Structure

```
nathreader/
├── src/
│   └── nathreader/         # Main package
│       ├── core/           # Core functionality
│       ├── ui/             # User interface components
│       ├── utils/          # Utility functions
│       ├── __init__.py
│       └── __main__.py     # Entry point
├── tests/                  # Test files
├── config/                 # Configuration files
├── scripts/                # Build and utility scripts
├── .gitignore
├── pyproject.toml          # Project metadata and dependencies
└── README.md
```

## 🛠️ Development

### Setting up the development environment
1. Fork and clone the repository
2. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -e .[dev]
   ```

### Running tests
```bash
pytest
```

### Building the application
1. Install build dependencies:
   ```bash
   pip install build
   ```

2. Build the package:
   ```bash
   python -m build
   ```

### Creating an installer
1. Install Inno Setup from https://jrsoftware.org/isdl.php
2. Run the build script:
   ```bash
   .\scripts\build.bat
   ```
3. The installer will be created in the `dist` directory

## Usage

- Open files using the File > Open menu or by double-clicking associated file types
- Use the search function (Ctrl+F) to find text within documents
- Add bookmarks to quickly navigate to important pages
- Print documents using the Print option in the File menu

## License

MIT License - Free for personal and commercial use
