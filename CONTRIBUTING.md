# Contributing

Thanks for your interest in winremote-mcp!

## Workflow

1. **Fork** the repo and clone locally
2. **Branch** from `master`: `git checkout -b feat/my-feature`
3. **Install dev deps**: `pip install -e ".[dev]"`
4. **Lint**: `ruff check . && ruff format --check .`
5. **Commit** using [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: add new tool`
   - `fix: handle missing window`
   - `chore: update deps`
6. **Push** and open a **Pull Request** against `master`
7. PRs are **squash merged**

## Development

```bash
# Run with hot reload
winremote-mcp --reload
```

## Code Style

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting. CI will check automatically.
