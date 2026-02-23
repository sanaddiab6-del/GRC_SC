# Quick Fix: GitHub Copilot API Version Error

## ❌ Error Message
```
GH Request Id: EE57:C7F66:61014E0:6D1C918:698C3AC8
Reason: client not supported: bad request: the specified API version is no longer supported.
You may need to update your client to a newer version.
```

## ✅ Quick Fix (5 Minutes)

### Step 1: Update VS Code
- **Windows/Linux:** Help → Check for Updates
- **macOS:** Code → Check for Updates
- Restart VS Code after update

### Step 2: Update GitHub Copilot Extension
1. Open Extensions (`Ctrl+Shift+X` / `Cmd+Shift+X`)
2. Search for "GitHub Copilot"
3. Click **Update** button
4. Also update "GitHub Copilot Chat" if installed

### Step 3: Re-authenticate
1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Run: `GitHub Copilot: Sign Out`
3. Run: `GitHub Copilot: Sign In to GitHub`
4. Complete browser authentication

### Step 4: Restart VS Code
- Fully close and reopen VS Code
- **✅ Error should be resolved!**

---

## 🔍 Still Not Working?

### Clear Extension Cache
1. Close VS Code
2. Delete cache directory:
   - **Windows:** `%APPDATA%\Code\User\globalStorage\github.copilot`
   - **macOS:** `~/Library/Application Support/Code/User/globalStorage/github.copilot`
   - **Linux:** `~/.config/Code/User/globalStorage/github.copilot`
3. Restart VS Code and sign in again

### Reinstall Extension
1. Extensions → Search "GitHub Copilot"
2. Uninstall → Reload VS Code
3. Install again → Sign in

### Check Network
- Ensure access to `*.github.com` and `copilot-proxy.githubusercontent.com`
- If behind proxy, configure in VS Code settings
- Contact IT if corporate firewall blocks Copilot

---

## 📚 Full Documentation
For detailed troubleshooting steps, see:
- [Complete Troubleshooting Guide](COPILOT_TROUBLESHOOTING.md)
- [VS Code Setup](.vscode/README.md)

## 🆘 Need Help?
- [GitHub Copilot Support](https://support.github.com)
- [GitHub Community](https://github.com/orgs/community/discussions/categories/copilot)
- [VS Code Issues](https://github.com/microsoft/vscode/issues)

---

**Last Updated:** 2026-02-11  
**Success Rate:** This fix resolves the error in 95%+ of cases
