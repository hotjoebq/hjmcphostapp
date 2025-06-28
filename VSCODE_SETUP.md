# VS Code Development Setup

This guide will help you set up the MCP Host Application for local development in Visual Studio Code.

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Visual Studio Code** with Python extension
3. **Git** for version control

## Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hotjoebq/hjmcphostapp.git
   cd hjmcphostapp
   ```

2. **Open in VS Code:**
   ```bash
   code .
   ```

3. **Install recommended extensions:**
   - VS Code will prompt you to install recommended extensions
   - Click "Install All" when prompted
   - Or manually install from the Extensions panel

4. **Set up Python environment:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # On Linux/Mac:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

5. **Install system dependencies (Linux/Mac only):**
   ```bash
   # For SQL Server connectivity
   sudo apt install unixodbc-dev  # Ubuntu/Debian
   # or
   brew install unixodbc          # macOS
   ```

## VS Code Configuration

The repository includes pre-configured VS Code settings:

### Launch Configurations (F5 to debug)
- **Run MCP Host Application** - Main application entry point
- **Run Remote MCP Client** - Test remote MCP client
- **Run SQL MCP Client** - Test SQL Server MCP client  
- **Run Internet MCP Client** - Test Internet Search MCP client
- **Run SQL Server MCP** - Start SQL Server MCP server
- **Run Internet MCP Server** - Start Internet Search MCP server

### Tasks (Ctrl+Shift+P → "Tasks: Run Task")
- **Install Dependencies** - Install Python packages
- **Install ODBC Drivers (Linux)** - Install SQL Server drivers
- **Run MCP Host Application** - Execute main application
- **Setup Development Environment** - Complete setup process

### Recommended Extensions
- Python (Microsoft) - Core Python support
- Pylance - Advanced Python language server
- Black Formatter - Code formatting
- isort - Import sorting
- Pylint - Code linting

## Running the Application

### Method 1: Using VS Code Debugger
1. Open `main.py`
2. Press `F5` or go to Run → Start Debugging
3. Select "Run MCP Host Application"

### Method 2: Using Tasks
1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select "Run MCP Host Application"

### Method 3: Using Terminal
1. Open VS Code terminal (`Ctrl+` `)
2. Run: `python3 main.py`

## Testing Individual Components

### Test Remote MCP Client
```bash
python3 clients/remote_client.py
```

### Test SQL MCP Client
```bash
python3 clients/sql_client.py
```

### Test Internet MCP Client
```bash
python3 clients/internet_client.py
```

## Debugging

1. **Set breakpoints** by clicking in the gutter next to line numbers
2. **Use F5** to start debugging with the selected configuration
3. **Use F10/F11** to step through code
4. **View variables** in the Debug panel
5. **Check logs** in the integrated terminal

## Troubleshooting

### Python Interpreter Not Found
1. Press `Ctrl+Shift+P`
2. Type "Python: Select Interpreter"
3. Choose your virtual environment Python

### ODBC Driver Issues (SQL Server)
```bash
# Linux
sudo apt install unixodbc-dev

# macOS
brew install unixodbc

# Windows
# Download Microsoft ODBC Driver for SQL Server
```

### Import Errors
1. Ensure virtual environment is activated
2. Install dependencies: `pip install -r requirements.txt`
3. Check PYTHONPATH is set correctly

### MCP Server Connection Issues
1. Check server logs in the terminal
2. Verify stdio communication is working
3. Test individual clients separately

## Project Structure

```
hjmcphostapp/
├── .vscode/                 # VS Code configuration
│   ├── launch.json         # Debug configurations
│   ├── settings.json       # Editor settings
│   ├── tasks.json          # Build/test tasks
│   └── extensions.json     # Recommended extensions
├── clients/                # MCP client implementations
│   ├── remote_client.py    # Remote MCP client
│   ├── sql_client.py       # SQL Server MCP client
│   └── internet_client.py  # Internet Search MCP client
├── servers/                # MCP server implementations
│   ├── sql_server_mcp.py   # SQL Server MCP server
│   └── internet_mcp.py     # Internet Search MCP server
├── main.py                 # Main application
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
└── VSCODE_SETUP.md        # This setup guide
```

## Development Workflow

1. **Make changes** to the code
2. **Test locally** using F5 or tasks
3. **Debug issues** using breakpoints
4. **Format code** automatically on save
5. **Commit changes** using VS Code Git integration

## Support

If you encounter issues:
1. Check the integrated terminal for error messages
2. Review the Debug Console for detailed logs
3. Ensure all dependencies are installed
4. Verify Python interpreter is correctly selected
