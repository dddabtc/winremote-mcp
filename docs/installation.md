# Installation Guide

## System Requirements

- **Operating System**: Windows 10 or Windows 11
- **Python**: 3.10 or higher
- **Memory**: 100MB+ available RAM
- **Network**: Optional (for remote access)

## Quick Installation

### From PyPI (Recommended)

```bash
pip install winremote-mcp
```

This installs the core package with all essential dependencies.

### From Source

```bash
git clone https://github.com/dddabtc/winremote-mcp.git
cd winremote-mcp
pip install .
```

## Optional Dependencies

### OCR Support

For text extraction from screenshots:

```bash
# Install Tesseract OCR engine
winget install UB-Mannheim.TesseractOCR

# Install Python dependencies
pip install winremote-mcp[ocr]
```

Supported OCR languages include:
- **English**: `eng` (default)
- **Chinese**: `chi_sim` (Simplified), `chi_tra` (Traditional)
- **Japanese**: `jpn`
- **Korean**: `kor`
- **100+ more languages** available

### Development Dependencies

```bash
pip install winremote-mcp[test]
```

## Verification

Test your installation:

```bash
# Check version
winremote-mcp --version

# Start server (should show "Server running on...")
winremote-mcp

# Health check (in another terminal)
curl http://localhost:8090/health
```

Expected output: `{"status":"ok","version":"0.4.4"}`

## Troubleshooting

### Python Version Issues

**Problem**: `ERROR: Python 3.9 is not supported`

**Solution**: Upgrade to Python 3.10+:
```bash
# Check current version
python --version

# Install Python 3.11 (recommended)
winget install Python.Python.3.11
```

### Permission Errors

**Problem**: `Access denied` when accessing registry/services

**Solution**: Run as Administrator:
1. Right-click Command Prompt
2. Select "Run as administrator"
3. Run `winremote-mcp`

### Port Already in Use

**Problem**: `OSError: [Errno 10048] Only one usage of each socket address`

**Solution**: Use a different port:
```bash
winremote-mcp --port 8091
```

Or find what's using port 8090:
```bash
netstat -ano | findstr :8090
taskkill /PID <pid> /F
```

### OCR Installation Issues

**Problem**: `pytesseract.TesseractNotFoundError`

**Solutions**:

1. **Install Tesseract via Winget** (recommended):
   ```bash
   winget install UB-Mannheim.TesseractOCR
   ```

2. **Manual installation**:
   - Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - Add to PATH: `C:\Program Files\Tesseract-OCR`

3. **Verify installation**:
   ```bash
   tesseract --version
   ```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'win32api'`

**Solution**: Install Windows-specific dependencies:
```bash
pip install pywin32
```

### Firewall Warnings

**Problem**: Windows Defender firewall popup when starting server

**Solution**: 
1. Click "Allow access" for private networks
2. Or run with localhost-only (default behavior):
   ```bash
   winremote-mcp  # Only accessible from 127.0.0.1
   ```

## Next Steps

Once installed successfully:

1. **Configure MCP Client**: See [Usage Guide](usage.md) for Claude Desktop, OpenClaw, or Cursor setup
2. **Enable Remote Access**: Use `--host 0.0.0.0 --auth-key "your-key"` for network access
3. **Auto-Start**: Run `winremote-mcp install` to start on boot

## Advanced Installation

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv winremote-env

# Activate (Windows)
winremote-env\Scripts\activate

# Install
pip install winremote-mcp
```

### Docker (Experimental)

!!! warning "Windows Container Limitations"
    Docker support requires Windows containers and has GUI limitations. Direct installation is recommended.

```dockerfile
# Dockerfile.windows
FROM mcr.microsoft.com/windows/servercore:ltsc2022
RUN pip install winremote-mcp
EXPOSE 8090
CMD ["winremote-mcp", "--host", "0.0.0.0"]
```

### Portable Installation

For USB/portable deployment:

```bash
# Install to specific directory
pip install --target ./winremote-portable winremote-mcp

# Run from portable directory
python -m winremote --transport stdio
```