"""OCR support — screenshot a region and extract text."""

from __future__ import annotations

import io
import subprocess
import tempfile
from pathlib import Path

from PIL import ImageGrab


def _screenshot_region(
    left: int | None = None,
    top: int | None = None,
    right: int | None = None,
    bottom: int | None = None,
) -> bytes:
    """Capture a region (or full screen) and return PNG bytes."""
    if left is not None and top is not None and right is not None and bottom is not None:
        img = ImageGrab.grab(bbox=(left, top, right, bottom))
    else:
        img = ImageGrab.grab()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def ocr_pytesseract(
    left: int | None = None,
    top: int | None = None,
    right: int | None = None,
    bottom: int | None = None,
    lang: str = "eng",
) -> str:
    """Run OCR using pytesseract."""
    try:
        import pytesseract
    except ImportError:
        raise ImportError(
            "pytesseract is not installed. Install it with:\n"
            "  pip install pytesseract\n"
            "You also need Tesseract-OCR installed:\n"
            "  Windows: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "  Then set TESSERACT_CMD or add to PATH."
        )

    if left is not None and top is not None and right is not None and bottom is not None:
        img = ImageGrab.grab(bbox=(left, top, right, bottom))
    else:
        img = ImageGrab.grab()

    text: str = pytesseract.image_to_string(img, lang=lang)
    return text.strip()


def ocr_windows_builtin(
    left: int | None = None,
    top: int | None = None,
    right: int | None = None,
    bottom: int | None = None,
) -> str:
    """Run OCR using Windows built-in OCR engine via PowerShell."""
    png_bytes = _screenshot_region(left, top, right, bottom)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(png_bytes)
        tmp_path = tmp.name

    ps_script = f"""
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType = WindowsRuntime]

# Helper to await WinRT async
Add-Type -TypeDefinition @'
using System;
using System.Threading.Tasks;
using System.Runtime.CompilerServices;
public static class AsyncHelper {{
    public static T Await<T>(Windows.Foundation.IAsyncOperation<T> op) {{
        return Task.Run(() => {{
            while (op.Status == Windows.Foundation.AsyncStatus.Started) {{
                System.Threading.Thread.Sleep(10);
            }}
            return op.GetResults();
        }}).Result;
    }}
}}
'@ -ReferencedAssemblies "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\System.Runtime.WindowsRuntime.dll"

$path = "{tmp_path.replace(chr(92), chr(92) + chr(92))}"
$stream = [System.IO.File]::OpenRead($path)
$ras = [System.IO.WindowsRuntimeStreamExtensions]::AsRandomAccessStream($stream)
$decoder = [AsyncHelper]::Await([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($ras))
$bitmap = [AsyncHelper]::Await($decoder.GetSoftwareBitmapAsync())
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
$result = [AsyncHelper]::Await($engine.RecognizeAsync($bitmap))
$stream.Close()
Write-Output $result.Text
"""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Windows OCR error: {e}"
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass


def run_ocr(
    left: int | None = None,
    top: int | None = None,
    right: int | None = None,
    bottom: int | None = None,
    lang: str = "eng",
) -> str:
    """Run OCR, trying pytesseract first, then Windows built-in."""
    errors = []
    # Try pytesseract first
    try:
        return ocr_pytesseract(left, top, right, bottom, lang=lang)
    except ImportError as e:
        errors.append(f"pytesseract: {e}")
    except Exception as e:
        errors.append(f"pytesseract error: {e}")

    # Fallback to Windows built-in OCR
    try:
        result = ocr_windows_builtin(left, top, right, bottom)
        if result and "error" not in result.lower()[:20]:
            return result
        if result:
            errors.append(f"Windows OCR: {result}")
    except Exception as e:
        errors.append(f"Windows OCR error: {e}")

    # Both failed
    return "OCR failed. Errors:\n" + "\n".join(errors)
