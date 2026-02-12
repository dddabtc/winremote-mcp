# API Reference

## Available Tools

WinRemote MCP provides 40+ tools organized into categories. All tools return structured responses with task IDs for monitoring.

## Desktop Control

### Snapshot
Capture screenshot with optional compression and window information.

**Parameters:**
- `quality` (int, 1-100): JPEG quality, default 85
- `max_width` (int): Resize width while preserving aspect ratio
- `monitor` (int): Monitor number (1, 2, etc.), default captures all

**Returns:**
- Base64 encoded JPEG image
- Window list with titles and positions
- UI element information

**Example:**
```json
{
  "tool": "Snapshot",
  "arguments": {
    "quality": 90,
    "max_width": 1920,
    "monitor": 1
  }
}
```

### Click
Perform mouse clicks at specified coordinates.

**Parameters:**
- `x` (int): X coordinate
- `y` (int): Y coordinate  
- `button` (str): "left", "right", or "middle", default "left"
- `clicks` (int): Number of clicks, default 1
- `action` (str): "click", "double", or "hover", default "click"

**Example:**
```json
{
  "tool": "Click", 
  "arguments": {
    "x": 500,
    "y": 300,
    "button": "left",
    "clicks": 2
  }
}
```

### Type
Type text at current cursor position or specified coordinates.

**Parameters:**
- `text` (str): Text to type
- `x` (int, optional): X coordinate to click before typing
- `y` (int, optional): Y coordinate to click before typing
- `interval` (float): Delay between keystrokes, default 0.01

### Scroll
Scroll vertically or horizontally.

**Parameters:**
- `x` (int): X coordinate for scroll center
- `y` (int): Y coordinate for scroll center
- `direction` (str): "up", "down", "left", "right"
- `clicks` (int): Number of scroll steps, default 3

### Move
Move mouse cursor or perform drag operations.

**Parameters:**
- `x` (int): Target X coordinate
- `y` (int): Target Y coordinate
- `drag` (bool): Whether to drag (hold button), default false
- `duration` (float): Movement duration in seconds, default 0.5

### Shortcut
Execute keyboard shortcuts.

**Parameters:**
- `keys` (str): Key combination (e.g., "ctrl+c", "alt+tab", "win+r")

**Examples:**
- `"ctrl+c"` - Copy
- `"alt+tab"` - Switch windows
- `"win+r"` - Run dialog
- `"ctrl+shift+esc"` - Task Manager

## Window Management

### FocusWindow
Bring a window to the foreground by title match.

**Parameters:**
- `title` (str): Window title (supports partial/fuzzy matching)

### MinimizeAll
Minimize all windows (equivalent to Win+D).

### App
Launch, focus, or resize applications.

**Parameters:**
- `action` (str): "launch", "focus", or "resize"
- `target` (str): Application name or executable path
- `width` (int, optional): Window width for resize
- `height` (int, optional): Window height for resize

## File Operations

### FileRead
Read text file contents.

**Parameters:**
- `path` (str): File path (supports environment variables)
- `encoding` (str): Text encoding, default "utf-8"

### FileWrite
Write content to a file.

**Parameters:**
- `path` (str): File path
- `content` (str): Content to write
- `encoding` (str): Text encoding, default "utf-8"
- `append` (bool): Append to file, default false

### FileList
List directory contents.

**Parameters:**
- `path` (str): Directory path
- `pattern` (str, optional): File pattern filter (e.g., "*.txt")
- `recursive` (bool): Include subdirectories, default false

### FileSearch
Search for files by name pattern.

**Parameters:**
- `path` (str): Search root directory
- `pattern` (str): File name pattern (supports wildcards)
- `recursive` (bool): Search subdirectories, default true

### FileDownload
Download file as base64 (for binary files).

**Parameters:**
- `path` (str): File path
- `max_size` (int): Maximum file size in bytes, default 10MB

### FileUpload
Upload file from base64 data.

**Parameters:**
- `path` (str): Destination file path
- `data` (str): Base64 encoded file content
- `overwrite` (bool): Overwrite existing file, default false

## System Administration

### Shell
Execute PowerShell commands.

**Parameters:**
- `command` (str): PowerShell command to execute
- `cwd` (str, optional): Working directory
- `timeout` (int): Timeout in seconds, default 30

### ListProcesses
List running processes with resource usage.

**Parameters:**
- `sort_by` (str): Sort field ("cpu", "memory", "name"), default "cpu"
- `limit` (int): Maximum number of processes, default 20

### KillProcess
Terminate a process by PID or name.

**Parameters:**
- `target` (str): Process PID (number) or name
- `force` (bool): Force kill, default false

### GetSystemInfo
Retrieve system information.

**Returns:**
- OS version and architecture
- CPU information and usage
- Memory statistics
- Disk space
- Network interfaces

### RegRead
Read Windows Registry value.

**Parameters:**
- `key` (str): Registry key path (e.g., "HKEY_LOCAL_MACHINE\\SOFTWARE\\...")
- `value` (str, optional): Value name (empty for default)

### RegWrite
Write Windows Registry value.

**Parameters:**
- `key` (str): Registry key path
- `value` (str): Value name
- `data` (str): Value data
- `type` (str): Value type ("REG_SZ", "REG_DWORD", etc.)

## Service Management

### ServiceList
List Windows services.

**Parameters:**
- `status` (str, optional): Filter by status ("running", "stopped", "all")

### ServiceStart
Start a Windows service.

**Parameters:**
- `name` (str): Service name

### ServiceStop
Stop a Windows service.

**Parameters:**
- `name` (str): Service name

## Scheduled Tasks

### TaskList
List Windows scheduled tasks.

**Parameters:**
- `folder` (str, optional): Task folder path, default "\"

### TaskCreate
Create a Windows scheduled task.

**Parameters:**
- `name` (str): Task name
- `command` (str): Command to execute
- `trigger` (str): When to run ("startup", "daily", "weekly", etc.)
- `user` (str, optional): User account, default current user

### TaskDelete
Delete a Windows scheduled task.

**Parameters:**
- `name` (str): Task name
- `folder` (str, optional): Task folder, default "\"

## Network Tools

### Ping
Ping a host to test connectivity.

**Parameters:**
- `host` (str): Hostname or IP address
- `count` (int): Number of ping attempts, default 4
- `timeout` (int): Timeout in seconds, default 5

### PortCheck
Check if a TCP port is open on a host.

**Parameters:**
- `host` (str): Hostname or IP address
- `port` (int): Port number
- `timeout` (int): Connection timeout, default 5

### NetConnections
List active network connections.

**Parameters:**
- `limit` (int): Maximum connections to return, default 50
- `filter` (str, optional): Filter by protocol ("tcp", "udp")

## Advanced Features

### OCR
Extract text from screen regions using OCR.

**Parameters:**
- `x1` (int): Top-left X coordinate
- `y1` (int): Top-left Y coordinate  
- `x2` (int): Bottom-right X coordinate
- `y2` (int): Bottom-right Y coordinate
- `lang` (str): OCR language, default "eng"

**Supported Languages:**
- `eng` - English
- `chi_sim` - Chinese Simplified
- `jpn` - Japanese
- `kor` - Korean
- Many more...

### ScreenRecord
Record screen activity as animated GIF.

**Parameters:**
- `duration` (int): Recording duration in seconds (2-10)
- `fps` (int): Frames per second, default 5
- `x` (int, optional): Recording region X
- `y` (int, optional): Recording region Y
- `width` (int, optional): Recording region width
- `height` (int, optional): Recording region height

### AnnotatedSnapshot
Take screenshot with numbered labels on interactive UI elements.

**Parameters:**
- `quality` (int): JPEG quality, default 85
- `max_width` (int, optional): Resize width

**Returns:**
- Annotated screenshot with red numbered labels
- List of UI elements with coordinates and descriptions

## Task Management

### GetRunningTasks
List all currently active tasks.

**Returns:**
- Task IDs and status for running/pending tasks
- Task start time and duration
- Task type and parameters

### GetTaskStatus
Get detailed information about a specific task.

**Parameters:**
- `task_id` (str, optional): Task ID to query (empty lists recent tasks)

### CancelTask
Cancel a running or pending task.

**Parameters:**
- `task_id` (str): Task ID to cancel

## Clipboard Operations

### GetClipboard
Read current clipboard content.

**Returns:**
- Text content from clipboard

### SetClipboard
Write content to clipboard.

**Parameters:**
- `text` (str): Text to copy to clipboard

## Notification System

### Notification
Display Windows toast notification.

**Parameters:**
- `title` (str): Notification title
- `message` (str): Notification message
- `duration` (int): Display duration in seconds, default 5

## Event Log

### EventLog
Read Windows Event Log entries.

**Parameters:**
- `log_name` (str): Log name ("System", "Application", "Security")
- `level` (str, optional): Filter by level ("Error", "Warning", "Information")
- `limit` (int): Maximum entries, default 10
- `hours` (int): Look back hours, default 24

## Authentication

For HTTP transport, include the Authorization header:

```http
Authorization: Bearer your-secret-key
```

The `/health` endpoint is always accessible without authentication.

## Error Responses

All tools return consistent error responses:

```json
{
  "success": false,
  "error": "Detailed error message",
  "task_id": "abc123"
}
```

## Response Format

Successful tool responses include:

```json
{
  "success": true,
  "result": "Tool-specific result data",
  "task_id": "abc123",
  "duration_ms": 150
}
```