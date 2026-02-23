# VS Code Workspace Configuration

This directory contains recommended VS Code settings and extensions for SICO GRC Platform development.

## Files

### `settings.json`
Workspace-specific settings including:
- **GitHub Copilot configuration** - Optimized for bilingual development
- **Python settings** - Black formatter, Flake8/MyPy linting, pytest integration
- **TypeScript/JavaScript settings** - Prettier formatter, ESLint
- **File exclusions** - Hide build artifacts and cache directories
- **Bilingual support** - UTF-8 encoding, proper line endings

### `extensions.json`
Recommended extensions for this project:
- **GitHub Copilot** & **Copilot Chat** - AI pair programming
- **Python** & **Pylance** - Python language support
- **ESLint** & **Prettier** - JavaScript/TypeScript tooling
- **Tailwind CSS IntelliSense** - CSS utility classes
- **Docker** & **Kubernetes** - Container development
- **SQLTools** - Database management
- **GitLens** - Enhanced Git integration
- **RTL Support** - Arabic language development

## Quick Setup

When you open this workspace in VS Code, you'll be prompted to install recommended extensions. Click **"Install All"** to get the full development environment.

### Manual Installation

If you need to manually install extensions:

```bash
# Install all recommended extensions at once
code --install-extension github.copilot
code --install-extension github.copilot-chat
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension bradlc.vscode-tailwindcss
code --install-extension ms-azuretools.vscode-docker
code --install-extension eamodio.gitlens
code --install-extension ahmadalli.vscode-rtl
```

## Troubleshooting

### GitHub Copilot Issues

If you encounter errors like:
- "client not supported: bad request: the specified API version is no longer supported"
- Copilot not providing suggestions
- Authentication failures

See the comprehensive [Copilot Troubleshooting Guide](../docs/development/COPILOT_TROUBLESHOOTING.md).

**Quick Fix:**
1. Update VS Code: Help → Check for Updates
2. Update Copilot: Extensions → Search "GitHub Copilot" → Update
3. Sign out and back in: Command Palette → "GitHub Copilot: Sign Out" → "Sign In"
4. Restart VS Code

### Python Environment Not Found

If VS Code can't find the Python interpreter:

1. Create virtual environment:
   ```bash
   cd src/backend
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

2. Select interpreter in VS Code:
   - Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
   - Type: "Python: Select Interpreter"
   - Choose: `./src/backend/.venv/bin/python`

### Prettier/ESLint Not Working

Ensure you've installed frontend dependencies:

```bash
cd src/frontend
npm install
```

Then reload VS Code window:
- Command Palette → "Developer: Reload Window"

## Settings Customization

To override workspace settings with your personal preferences:
1. Open User Settings (`Ctrl+,` / `Cmd+,`)
2. Your user settings will override workspace settings
3. Settings precedence: User Settings > Workspace Settings > Default Settings

### Common Overrides

**Disable format on save:**
```json
{
  "editor.formatOnSave": false
}
```

**Change Python formatter:**
```json
{
  "python.formatting.provider": "autopep8"
}
```

**Adjust Copilot trigger:**
```json
{
  "github.copilot.enable": {
    "*": false,
    "python": true,
    "typescript": true
  }
}
```

## Project-Specific Notes

### Bilingual Development
- Arabic text requires RTL (Right-to-Left) support
- Use `ahmadalli.vscode-rtl` extension for proper rendering
- All strings should use i18n keys, not hardcoded text

### Python Path Setup
The default Python interpreter path assumes:
```
src/backend/.venv/bin/python
```

If your virtual environment is elsewhere, update `settings.json`:
```json
{
  "python.defaultInterpreterPath": "/path/to/your/venv/bin/python"
}
```

### Testing Integration
- **Python tests**: Use Testing panel (beaker icon) or `pytest` in terminal
- **Frontend tests**: Run `npm test` in `src/frontend/`
- **E2E tests**: See [docs/testing/](../docs/testing/) for Playwright setup

## Resources

- [VS Code Documentation](https://code.visualstudio.com/docs)
- [Python in VS Code](https://code.visualstudio.com/docs/languages/python)
- [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- [VS Code Can Do That?](https://vscodecandothat.com/)

## Contributing

If you find issues with the workspace configuration or have suggestions:
1. Open an issue in the repository
2. Submit a pull request with improvements
3. Discuss in team channels

---

**Last Updated:** 2026-02-11  
**Maintainer:** SICO GRC Platform Team
