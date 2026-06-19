# WinRemote MCP 中文说明

[English README](README.md)

## v0.4.23 中文发布说明

### FastMCP debug/uvicorn 兼容性修复

- 修复 FastMCP 3.2.4+ 中 `run_http_async` 参数从 `uvicorn_args` 改为 `uvicorn_config` 后，`winremote-mcp --debug` 启动时报错的问题。
- 现在会自动检测当前 FastMCP 支持的参数名，并继续把 uvicorn 的 DEBUG 日志配置传递给 HTTP 传输层；旧版 FastMCP 仍保持兼容。
- 已添加回归测试，覆盖新旧 uvicorn 配置参数的兼容路径。
