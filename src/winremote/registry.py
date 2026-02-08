"""Windows Registry operations."""

from __future__ import annotations

import sys

if sys.platform == "win32":
    import winreg

    HAS_WINREG = True
else:
    HAS_WINREG = False

_ROOT_KEYS = {
    "HKCR": getattr(globals().get("winreg"), "HKEY_CLASSES_ROOT", None),
    "HKEY_CLASSES_ROOT": getattr(globals().get("winreg"), "HKEY_CLASSES_ROOT", None),
    "HKCU": getattr(globals().get("winreg"), "HKEY_CURRENT_USER", None),
    "HKEY_CURRENT_USER": getattr(globals().get("winreg"), "HKEY_CURRENT_USER", None),
    "HKLM": getattr(globals().get("winreg"), "HKEY_LOCAL_MACHINE", None),
    "HKEY_LOCAL_MACHINE": getattr(globals().get("winreg"), "HKEY_LOCAL_MACHINE", None),
    "HKU": getattr(globals().get("winreg"), "HKEY_USERS", None),
    "HKEY_USERS": getattr(globals().get("winreg"), "HKEY_USERS", None),
    "HKCC": getattr(globals().get("winreg"), "HKEY_CURRENT_CONFIG", None),
    "HKEY_CURRENT_CONFIG": getattr(globals().get("winreg"), "HKEY_CURRENT_CONFIG", None),
}

_REG_TYPES = {
    "REG_SZ": getattr(globals().get("winreg"), "REG_SZ", None),
    "REG_EXPAND_SZ": getattr(globals().get("winreg"), "REG_EXPAND_SZ", None),
    "REG_DWORD": getattr(globals().get("winreg"), "REG_DWORD", None),
    "REG_QWORD": getattr(globals().get("winreg"), "REG_QWORD", None),
    "REG_BINARY": getattr(globals().get("winreg"), "REG_BINARY", None),
    "REG_MULTI_SZ": getattr(globals().get("winreg"), "REG_MULTI_SZ", None),
}


def _parse_key(key: str) -> tuple:
    """Parse 'HKLM\\SOFTWARE\\...' into (root_handle, subkey_path)."""
    parts = key.split("\\", 1)
    root_name = parts[0].upper()
    subkey = parts[1] if len(parts) > 1 else ""
    root = _ROOT_KEYS.get(root_name)
    if root is None:
        raise ValueError(f"Unknown root key: {root_name}. Use HKCR, HKCU, HKLM, HKU, or HKCC.")
    return root, subkey


def reg_read(key: str, value_name: str) -> str:
    """Read a registry value."""
    if not HAS_WINREG:
        return "Error: Registry operations only available on Windows."
    try:
        root, subkey = _parse_key(key)
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ) as k:
            data, reg_type = winreg.QueryValueEx(k, value_name)
            return f"Value: {data!r} (type: {reg_type})"
    except FileNotFoundError:
        return f"Error: Key or value not found: {key}\\{value_name}"
    except Exception as e:
        return f"RegRead error: {e}"


def reg_write(key: str, value_name: str, data: str, reg_type: str = "REG_SZ") -> str:
    """Write a registry value."""
    if not HAS_WINREG:
        return "Error: Registry operations only available on Windows."
    try:
        root, subkey = _parse_key(key)
        rtype = _REG_TYPES.get(reg_type.upper())
        if rtype is None:
            return f"Error: Unknown type '{reg_type}'. Use: {', '.join(_REG_TYPES.keys())}"

        # Convert data based on type
        if reg_type.upper() == "REG_DWORD":
            data = int(data)
        elif reg_type.upper() == "REG_QWORD":
            data = int(data)
        elif reg_type.upper() == "REG_MULTI_SZ":
            data = data.split("|")

        with winreg.CreateKey(root, subkey) as k:
            winreg.SetValueEx(k, value_name, 0, rtype, data)
            return f"Written {value_name} = {data!r} to {key}"
    except Exception as e:
        return f"RegWrite error: {e}"
