# AI Vision Guide: Working with Non-Standard UI Frameworks

## The Problem

winremote-mcp uses Win32 API (`EnumChildWindows`) to detect interactive UI elements in `Snapshot` and `AnnotatedSnapshot`. This works well for standard Windows controls (WinForms, WPF, native Win32), but **fails for modern frameworks** that render their own UI:

- **Flutter** apps (e.g., YepFast, Google apps)
- **Electron** apps (VS Code, Discord, Slack, Notion)
- **Qt** applications (VLC, OBS, Telegram Desktop)
- **CEF/Chromium** embedded browsers
- **Custom-drawn UIs** (games, proprietary software)

These frameworks bypass native Windows controls, so Win32 enumeration returns zero elements. You'll see `AnnotatedSnapshot` report "No interactive elements found" even though the screen clearly shows buttons and inputs.

## Solution: AI Vision

The solution is to use the **AI's own vision capability** to understand the screenshot, rather than relying on Win32 API element detection. This guide covers three approaches, from simplest to most advanced.

---

## Approach 1: Use Snapshot + Claude's Built-in Vision (Recommended)

**No setup needed.** Claude (and other vision-capable LLMs) can directly "see" the screenshot returned by `Snapshot` and determine where to click.

### How It Works

```
┌─────────────────────────────────────────────┐
│  Claude Desktop / MCP Client                │
│                                             │
│  1. Call Snapshot() ─────────────────────►  │
│  2. Receive screenshot image ◄──────────    │
│  3. Claude's vision analyzes the image      │
│  4. Identifies "Connect" button at (520,340)│
│  5. Call Click(x=520, y=340) ──────────►    │
└─────────────────────────────────────────────┘
```

### Example Conversation

**You:** Open YepFast and click the connect button.

**Claude's internal process:**
1. Calls `Snapshot()` → receives screenshot showing YepFast (a Flutter app)
2. `AnnotatedSnapshot` would fail (Flutter has no Win32 controls), but regular `Snapshot` returns the visual screenshot
3. Claude's vision sees the "Connect" button in the screenshot
4. Calls `Click(x=520, y=340)` at the identified coordinates

### Tips for Best Results

```
# Ask Claude to use Snapshot (not AnnotatedSnapshot) for non-standard UIs
"Take a screenshot with Snapshot and find the login button, then click it."

# Be specific about what you want Claude to find
"Take a screenshot. I need you to find the blue 'Sign In' button 
in the bottom-right area, then click it."

# For complex UIs, use a two-step approach
"First take a screenshot so I can see what's on screen."
"Now click the third item in the sidebar menu."
```

### When to Use This Approach

- You're using Claude Desktop, Cursor, or any vision-capable MCP client
- Simple to moderate UI interactions
- No additional setup or GPU required
- Works with any visible UI element on screen

---

## Approach 2: Companion MCP Server — UI-TARS Desktop

For advanced automation that needs **dedicated visual AI grounding** (e.g., batch automation, complex multi-step workflows, non-Claude clients), use [UI-TARS Desktop](https://github.com/bytedance/UI-TARS-desktop) as a companion MCP server.

### Why UI-TARS?

| Metric | Value |
|--------|-------|
| ScreenSpot-Pro accuracy | **67.8%** (open-source SOTA) |
| ScreenSpot-V2 accuracy | **94.2%** |
| Chinese UI support | **Excellent** (ByteDance-trained) |
| License | Apache 2.0 |
| GPU requirement | ~16-18 GB VRAM (7B model) |

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Claude Desktop                                              │
│                                                              │
│  MCP Server 1: winremote-mcp     MCP Server 2: UI-TARS      │
│  ├── Snapshot (screenshot)       ├── Visual grounding        │
│  ├── Click / Type / Scroll       ├── Element detection       │
│  ├── Shell / FileRead            └── Semantic search         │
│  └── ... (40+ executor tools)                                │
│                                                              │
│  Workflow:                                                   │
│  1. UI-TARS analyzes screenshot → finds element coordinates  │
│  2. winremote-mcp executes Click/Type at those coordinates   │
└──────────────────────────────────────────────────────────────┘
```

### Setup

1. **Install UI-TARS Desktop:**
   ```bash
   # Download from https://github.com/bytedance/UI-TARS-desktop/releases
   # Or build from source:
   git clone https://github.com/bytedance/UI-TARS-desktop.git
   cd UI-TARS-desktop
   npm install && npm run build
   ```

2. **Configure Claude Desktop** with both MCP servers:
   ```json
   {
     "mcpServers": {
       "winremote": {
         "type": "http",
         "url": "http://localhost:8090/mcp/"
       },
       "ui-tars": {
         "type": "http",
         "url": "http://localhost:1234/mcp/"
       }
     }
   }
   ```

3. **Use both together:**
   ```
   "Use UI-TARS to find the 'Connect' button in the YepFast window,
    then use winremote Click to click it."
   ```

---

## Approach 3: Companion MCP Server — OmniMCP (OmniParser)

[OmniMCP](https://github.com/OpenAdaptAI/OmniMCP) wraps Microsoft's [OmniParser V2](https://github.com/microsoft/OmniParser) into an MCP server. OmniParser is a pure-vision screen parser that detects all interactable elements via YOLO + Florence2 models.

### Why OmniParser?

| Metric | Value |
|--------|-------|
| Approach | YOLO element detection + Florence2 captioning |
| Speed | 0.6-0.8s per screenshot (on A100/RTX 4090) |
| License | MIT (code), AGPL (YOLO model) |
| GPU requirement | ~16-18 GB VRAM |
| LLM-agnostic | Yes — pairs with any LLM (Claude, GPT, Gemini, Ollama) |

### Setup

```bash
pip install omnimcp

# Or run via Docker
docker run -p 8080:8080 omnimcp/server
```

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "winremote": {
      "type": "http",
      "url": "http://localhost:8090/mcp/"
    },
    "omnimcp": {
      "type": "http",
      "url": "http://localhost:8080/mcp/"
    }
  }
}
```

---

## Comparison: Which Approach to Choose?

| | Approach 1: Claude Vision | Approach 2: UI-TARS | Approach 3: OmniMCP |
|---|:---:|:---:|:---:|
| **Setup effort** | None | Medium | Medium |
| **GPU required** | No | Yes (~16 GB) | Yes (~16 GB) |
| **Accuracy** | Good (87.6% SV2) | Best (94.2% SV2) | Good (with LLM) |
| **Chinese UI** | Good | **Best** | Moderate |
| **Latency** | 2-5s (API) | 1-3s (local) | 0.6s + LLM time |
| **Offline** | No | Yes | Yes |
| **Cost** | Claude API tokens | Free (self-hosted) | Free (self-hosted) |
| **Best for** | Most users | Power users / automation | Multi-LLM setups |

### Decision Tree

```
Do you need to handle non-Win32 UIs?
├── No → Use AnnotatedSnapshot as usual
└── Yes
    ├── Are you using Claude / GPT-4V as your MCP client?
    │   ├── Yes → Approach 1 (Snapshot + LLM vision). Start here.
    │   └── No → Approach 2 or 3
    ├── Do you need the highest accuracy + Chinese UI?
    │   └── Yes → Approach 2 (UI-TARS)
    └── Do you need to work with multiple LLM backends?
        └── Yes → Approach 3 (OmniMCP)
```

---

## FAQ

### Q: Why doesn't winremote-mcp integrate a vision model directly?

winremote-mcp is designed as a **stable executor** — it does screenshot/click/type/shell operations reliably. Vision understanding belongs to the **caller-side LLM reasoning layer** (Claude, GPT, etc.) or a dedicated vision service. This separation:

- Keeps winremote-mcp lightweight (no 16 GB GPU requirement)
- Avoids coupling to specific model providers
- Lets you choose the best vision tool for your use case
- Maintains a clean executor/reasoner architecture

### Q: Does AnnotatedSnapshot work with Electron apps?

Partially. Some Electron apps expose accessibility tree elements via Chromium's native Windows support. Try `AnnotatedSnapshot` first — if it finds elements, great. If not, fall back to `Snapshot` + AI vision (Approach 1).

### Q: Can I use this with a local LLM (Ollama, etc.)?

Yes. Use Approach 2 (UI-TARS) or Approach 3 (OmniMCP) for fully local, offline operation. Both support running on a local GPU without any cloud API.

### Q: What about screen recording with non-standard UIs?

`ScreenRecord` captures the raw screen as GIF regardless of the UI framework — it works with everything. The limitation is only in **element detection** (AnnotatedSnapshot), not in visual capture.
