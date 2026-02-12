# Contributing to WinRemote MCP

Thank you for your interest in contributing to WinRemote MCP! This guide will help you get started.

## Development Setup

### Prerequisites

- **Windows 10/11** (for testing Windows-specific features)
- **Python 3.10+**
- **Git**
- **Code editor** (VS Code, PyCharm, etc.)

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/dddabtc/winremote-mcp.git
cd winremote-mcp

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Install in development mode
pip install -e ".[test,dev,ocr]"

# Run tests to verify setup
pytest
```

### Project Structure

```
winremote-mcp/
├── src/winremote/           # Main package
│   ├── __init__.py
│   ├── __main__.py          # CLI entry point
│   ├── server.py            # FastMCP server
│   ├── tools/               # MCP tools
│   │   ├── desktop.py       # Desktop control tools
│   │   ├── files.py         # File operation tools
│   │   ├── system.py        # System administration tools
│   │   └── network.py       # Network tools
│   ├── utils/               # Utility modules
│   └── taskmanager.py       # Task management
├── tests/                   # Test suite
├── docs/                    # Documentation
├── skill/                   # Platform integrations
└── pyproject.toml          # Project configuration
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Changes

- **Add new tools**: Create in appropriate file under `src/winremote/tools/`
- **Fix bugs**: Focus on minimal, targeted changes
- **Update docs**: Keep documentation in sync with code changes

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_desktop_tools.py

# Run with coverage
pytest --cov=winremote --cov-report=term-missing

# Test manually
python -m winremote --transport stdio
```

### 4. Format Code

```bash
# Format with ruff
ruff format .

# Check for issues
ruff check .
```

### 5. Commit and Push

```bash
git add .
git commit -m "feat: add new screenshot compression feature"
git push origin feature/your-feature-name
```

### 6. Create Pull Request

- Go to GitHub and create a pull request
- Fill out the PR template
- Link any related issues

## Adding New Tools

### Tool Structure

Each MCP tool follows this pattern:

```python
from typing import Dict, Any, List
from ..taskmanager import task_manager

@task_manager.tool(category="desktop")  # or "file", "query", "shell", "network"
def tool_name(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Brief description of what this tool does.
    
    Args:
        param1: Description of parameter
        param2: Optional parameter with default
        
    Returns:
        Dict containing tool result
        
    Raises:
        ValueError: When parameters are invalid
    """
    try:
        # Tool implementation
        result = do_something(param1, param2)
        
        return {
            "success": True,
            "result": result,
            "message": f"Successfully processed {param1}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to process {param1}"
        }
```

### Tool Categories

Tools are organized into categories that determine concurrency limits:

- **desktop**: Mouse, keyboard, screenshot (exclusive - one at a time)
- **file**: File operations (max 3 concurrent)  
- **query**: Read-only system queries (max 5 concurrent)
- **shell**: Command execution (max 2 concurrent)
- **network**: Network operations (max 3 concurrent)

### Adding a New Tool

1. **Choose the right file**: Add to appropriate file in `src/winremote/tools/`
2. **Import dependencies**: Add any new dependencies to `pyproject.toml`
3. **Write the tool**: Follow the structure above
4. **Add tests**: Create test in `tests/` directory
5. **Update docs**: Add to API reference

**Example - Adding a new file tool:**

```python
# src/winremote/tools/files.py

@task_manager.tool(category="file")
def file_hash(path: str, algorithm: str = "md5") -> Dict[str, Any]:
    """
    Calculate hash of a file.
    
    Args:
        path: File path
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        Dict with file hash and metadata
    """
    import hashlib
    from pathlib import Path
    
    try:
        if algorithm not in ["md5", "sha1", "sha256"]:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
            
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
            
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
                
        return {
            "success": True,
            "result": {
                "file": str(file_path),
                "algorithm": algorithm, 
                "hash": hash_func.hexdigest(),
                "size": file_path.stat().st_size
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

## Writing Tests

### Test Structure

Tests use `unittest.mock` to simulate Windows APIs, so they run on any platform.

```python
# tests/test_new_feature.py

import pytest
from unittest.mock import patch, Mock
from winremote.tools.files import file_hash

class TestFileHash:
    
    @patch('winremote.tools.files.Path')
    @patch('winremote.tools.files.open')
    def test_file_hash_md5(self, mock_open, mock_path):
        # Setup mocks
        mock_file_path = Mock()
        mock_file_path.exists.return_value = True
        mock_file_path.stat.return_value.st_size = 1024
        mock_path.return_value = mock_file_path
        
        mock_file = Mock()
        mock_file.read.side_effect = [b"test data", b""]
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Test the tool
        result = file_hash("test.txt", "md5")
        
        # Assertions
        assert result["success"] is True
        assert "hash" in result["result"]
        assert result["result"]["algorithm"] == "md5"
        assert result["result"]["size"] == 1024
        
    def test_file_hash_invalid_algorithm(self):
        result = file_hash("test.txt", "invalid")
        
        assert result["success"] is False
        assert "Unsupported algorithm" in result["error"]
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_new_feature.py::TestFileHash::test_file_hash_md5

# Run with verbose output  
pytest -v

# Run with coverage
pytest --cov=winremote --cov-report=html
```

## Documentation

### API Documentation

When adding new tools, update `docs/api.md`:

```markdown
### FileHash
Calculate hash of a file for integrity verification.

**Parameters:**
- `path` (str): File path
- `algorithm` (str): Hash algorithm ("md5", "sha1", "sha256"), default "md5"

**Returns:**
- File path, algorithm, hash value, and file size

**Example:**
\```json
{
  "tool": "FileHash",
  "arguments": {
    "path": "C:\\Users\\user\\document.pdf", 
    "algorithm": "sha256"
  }
}
\```
```

### Code Documentation

Use Google-style docstrings:

```python
def complex_function(param1: str, param2: List[int], param3: bool = False) -> Dict[str, Any]:
    """
    Brief one-line description.
    
    More detailed explanation of what this function does, why it exists,
    and any important behavioral details.
    
    Args:
        param1: Description of first parameter
        param2: List of integers for processing
        param3: Optional flag to enable special behavior
        
    Returns:
        Dictionary containing:
            - success: Whether operation succeeded
            - result: The main result data
            - metadata: Additional information
            
    Raises:
        ValueError: When param1 is empty or param2 contains negative numbers
        FileNotFoundError: When referenced files don't exist
        
    Example:
        >>> result = complex_function("test", [1, 2, 3], True)
        >>> print(result["success"])
        True
    """
```

## Code Style

### Python Style

We use `ruff` for formatting and linting:

```bash
# Format code
ruff format .

# Check for style issues
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### Key Style Guidelines

- **Line length**: 120 characters max
- **Imports**: Use absolute imports, group stdlib/third-party/local
- **Type hints**: Use for all function parameters and return values
- **Docstrings**: Google style for all public functions
- **Error handling**: Always handle exceptions gracefully

### Example

```python
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from ..taskmanager import task_manager

logger = logging.getLogger(__name__)

@task_manager.tool(category="file")
def process_files(
    directory: str, 
    pattern: str = "*.txt", 
    recursive: bool = False
) -> Dict[str, Any]:
    """
    Process files in a directory matching the given pattern.
    
    Args:
        directory: Target directory path
        pattern: File matching pattern with wildcards
        recursive: Whether to search subdirectories
        
    Returns:
        Dict containing processed file information
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
            
        # Implementation here...
        
    except Exception as e:
        logger.error(f"Failed to process files: {e}")
        return {"success": False, "error": str(e)}
```

## Platform Integration

### Adding New Platform Support

To add support for a new MCP client platform:

1. **Create skill directory**: `skill/platform-name/`
2. **Add configuration files**: Platform-specific MCP config
3. **Write integration guide**: `skill/platform-name/README.md`
4. **Test thoroughly**: Verify all tools work correctly

**Example structure:**
```
skill/new-platform/
├── README.md              # Setup guide
├── mcp-config.json        # MCP configuration
├── SKILL.md              # Platform-specific skill info
└── examples/             # Usage examples
```

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **Major** (1.0.0): Breaking changes
- **Minor** (0.2.0): New features, backward compatible
- **Patch** (0.1.1): Bug fixes, backward compatible

### Preparing a Release

1. **Update version** in `pyproject.toml`
2. **Update changelog** in `CHANGELOG.md`
3. **Run full test suite**: `pytest`
4. **Test on clean environment**: Fresh virtual environment
5. **Update documentation**: Ensure all docs are current

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version bumped in `pyproject.toml`
- [ ] `CHANGELOG.md` updated
- [ ] No TODO/FIXME comments in released code
- [ ] Integration tests pass on actual Windows system

## Getting Help

### Resources

- **GitHub Issues**: [github.com/dddabtc/winremote-mcp/issues](https://github.com/dddabtc/winremote-mcp/issues)
- **Discussions**: GitHub Discussions for questions and ideas
- **Code Review**: All PRs get reviewed before merging

### Communication

- **Be respectful**: Follow the code of conduct
- **Be specific**: Include error messages, OS version, Python version
- **Be patient**: This is an open-source project maintained by volunteers

## Code of Conduct

### Our Standards

- **Be welcoming**: Help newcomers feel included
- **Be respectful**: Disagreements are OK, personal attacks are not  
- **Be constructive**: Focus on improving the project
- **Be collaborative**: Work together toward common goals

### Unacceptable Behavior

- Harassment, discrimination, or exclusionary behavior
- Personal attacks or inflammatory comments
- Publishing private information without consent
- Trolling, insulting comments, or deliberate disruption

### Enforcement

Project maintainers will address violations of the code of conduct. Consequences may include warnings, temporary bans, or permanent bans depending on severity.

---

**Thank you for contributing to WinRemote MCP!** 🎉 

Your contributions help make Windows automation more accessible to AI agents and developers worldwide.