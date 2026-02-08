# OCR Setup Guide

winremote-mcp's OCR tool supports two engines. It tries them in order:

1. **pytesseract** (recommended) — open-source, accurate, multi-language
2. **Windows built-in OCR** (fallback) — no install needed on Windows 10+, limited

## Option 1: pytesseract (Recommended)

### Step 1: Install Tesseract-OCR Engine

**Windows (installer):**
1. Download from https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (e.g. `tesseract-ocr-w64-setup-5.x.x.exe`)
3. During install, select additional languages if needed (Chinese, Japanese, etc.)
4. Default install path: `C:\Program Files\Tesseract-OCR`

**Windows (winget):**
```bash
winget install UB-Mannheim.TesseractOCR
```

**Windows (chocolatey):**
```bash
choco install tesseract
```

### Step 2: Add to PATH

Make sure `tesseract.exe` is in your system PATH:
```powershell
# Check if it's accessible
tesseract --version

# If not, add to PATH:
$env:PATH += ";C:\Program Files\Tesseract-OCR"
# Or set permanently via System Properties → Environment Variables
```

Alternatively, set the `TESSERACT_CMD` environment variable:
```powershell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### Step 3: Install Python package

```bash
pip install winremote-mcp[ocr]
# or separately:
pip install pytesseract
```

### Step 4: Verify

```python
import pytesseract
print(pytesseract.get_tesseract_version())
```

### Language Support

Tesseract supports 100+ languages. During installation, select the ones you need.

Common language codes:
| Code | Language |
|------|----------|
| `eng` | English (default) |
| `chi_sim` | Simplified Chinese |
| `chi_tra` | Traditional Chinese |
| `jpn` | Japanese |
| `kor` | Korean |
| `deu` | German |
| `fra` | French |
| `spa` | Spanish |

Use the `lang` parameter in the OCR tool:
```
OCR(lang="chi_sim")       # Chinese
OCR(lang="eng+chi_sim")   # English + Chinese
```

List installed languages:
```bash
tesseract --list-langs
```

## Option 2: Windows Built-in OCR (Fallback)

Windows 10/11 includes a built-in OCR engine (`Windows.Media.Ocr`). No installation required.

### How it works

When pytesseract is not available, the OCR tool automatically falls back to Windows built-in OCR via PowerShell. It uses the `Windows.Media.Ocr.OcrEngine` WinRT API.

### Limitations

- **Language detection is automatic** — uses your Windows language settings
- **Less accurate** than pytesseract for complex layouts
- **Slower** — invokes PowerShell subprocess
- **No `lang` parameter** — uses system profile languages
- **May fail on older Windows 10 builds** — requires Windows 10 1809+

### Adding Languages (Windows OCR)

Windows OCR uses the languages installed on your system:

1. Open **Settings → Time & Language → Language**
2. Click **Add a language**
3. Select the language you need
4. Make sure **Basic typing** or **Handwriting** is installed (includes OCR)

### Troubleshooting Windows OCR

If Windows OCR returns empty results:

1. **Check Windows version**: Run `winver` — need Windows 10 1809+
2. **Check installed languages**:
   ```powershell
   Get-WinUserLanguageList
   ```
3. **Test OCR directly**:
   ```powershell
   # This should load without errors
   Add-Type -AssemblyName System.Runtime.WindowsRuntime
   [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
   ```
4. **.NET Framework**: Ensure .NET Framework 4.7.2+ is installed

## Usage Examples

### Full screen OCR
```
OCR()
```

### Region OCR (specific area)
```
OCR(left=100, top=200, right=500, bottom=400)
```

### Chinese text
```
OCR(lang="chi_sim")
```

### Workflow: Screenshot → OCR → Click

1. `Snapshot` — see what's on screen
2. `OCR(left=x1, top=y1, right=x2, bottom=y2)` — read text in a region
3. `Click(x, y)` — click on the identified element

### Workflow: AnnotatedSnapshot → OCR

1. `AnnotatedSnapshot` — get labeled screenshot with element positions
2. Identify the element with text you want to read
3. `OCR(left, top, right, bottom)` — extract text from that element's region

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "pytesseract is not installed" | `pip install pytesseract` |
| "tesseract is not installed or not in PATH" | Install Tesseract-OCR and add to PATH |
| Empty results with pytesseract | Check image quality, try different `lang` |
| Empty results with Windows OCR | Check Windows language pack installation |
| Both engines fail | Verify screenshot works first with `Snapshot` |
| Chinese characters garbled | Install `chi_sim` language pack for Tesseract |
