# GitHub Copilot Troubleshooting Guide

## Common Error: "client not supported: bad request: the specified API version is no longer supported"

### What This Error Means
This error appears in VS Code when your GitHub Copilot extension or VS Code client is using an outdated API version that GitHub has deprecated. This is a **client-side issue** that requires updating your local development environment.

**Error Message Format:**
```
GH Request Id: [ID]
Reason: client not supported: bad request: the specified API version is no longer supported. 
You may need to update your client to a newer version.
```

---

## Quick Fix (Try These First)

### 1. Update VS Code and Copilot Extension
This resolves the issue in 90% of cases.

**Steps:**
1. **Update VS Code:**
   - Help → Check for Updates (or download from [code.visualstudio.com](https://code.visualstudio.com/))
   - Requires restart after update

2. **Update GitHub Copilot Extension:**
   - Open Extensions panel (`Ctrl+Shift+X` / `Cmd+Shift+X`)
   - Search for "GitHub Copilot"
   - Click "Update" if available
   - Also update "GitHub Copilot Chat" if installed

3. **Restart VS Code completely**

---

### 2. Sign Out and Back In
Refreshes your authentication token with the latest API version.

**Steps:**
1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Type: `GitHub Copilot: Sign Out`
3. Execute the command
4. Type: `GitHub Copilot: Sign In to GitHub`
5. Complete the authentication flow in your browser
6. Restart VS Code

---

### 3. Clear Copilot Extension Cache
Removes potentially corrupted cached data.

**Steps:**
1. Close VS Code completely
2. Navigate to your VS Code data directory:
   - **Windows:** `%APPDATA%\Code\User\globalStorage\github.copilot`
   - **macOS:** `~/Library/Application Support/Code/User/globalStorage/github.copilot`
   - **Linux:** `~/.config/Code/User/globalStorage/github.copilot`
3. Delete the `github.copilot` folder
4. Restart VS Code
5. Sign in to Copilot again

---

### 4. Reinstall Copilot Extension
Complete clean install of the extension.

**Steps:**
1. Open Extensions panel (`Ctrl+Shift+X` / `Cmd+Shift+X`)
2. Search for "GitHub Copilot"
3. Click "Uninstall"
4. Reload VS Code when prompted
5. Search for "GitHub Copilot" again
6. Click "Install"
7. Sign in when prompted

---

## Advanced Troubleshooting

### Check Network/Firewall/Proxy Settings
Corporate networks may block Copilot API endpoints.

**Required Endpoints:**
- `*.github.com`
- `copilot-proxy.githubusercontent.com`
- `api.github.com`

**If using a proxy:**
1. Configure VS Code proxy settings:
   ```json
   {
     "http.proxy": "http://proxy.company.com:8080",
     "http.proxyStrictSSL": false
   }
   ```
2. Or set environment variables:
   ```bash
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

**Corporate firewall:**
- Contact your IT department to whitelist GitHub Copilot endpoints
- Some organizations block AI coding assistants by policy

---

### Verify Copilot Subscription Status
Ensure your Copilot license is active.

**Steps:**
1. Visit [github.com/settings/copilot](https://github.com/settings/copilot)
2. Verify your subscription status
3. Check if your organization has Copilot enabled
4. Ensure payment is up to date

---

### Check VS Code and Extension Versions

**Minimum Requirements:**
- **VS Code:** 1.85.0 or higher (1.90.0+ recommended)
- **GitHub Copilot:** Latest version (check monthly for updates)
- **Node.js:** 18.x or higher (if building extensions)

**Check your versions:**
```bash
# VS Code version
code --version

# List installed extensions with versions
code --list-extensions --show-versions | grep copilot
```

---

### Enable Copilot Debug Logging
Helps diagnose persistent issues.

**Steps:**
1. Open VS Code Settings (`Ctrl+,` / `Cmd+,`)
2. Search for: `github.copilot.advanced`
3. Enable: `Github > Copilot: Advanced > Debug`
4. Open Output panel (`Ctrl+Shift+U` / `Cmd+Shift+U`)
5. Select "GitHub Copilot" from dropdown
6. Reproduce the error and check logs

**Common log patterns to look for:**
- `401 Unauthorized` → Authentication issue (sign out/in)
- `403 Forbidden` → Subscription or permission issue
- `429 Too Many Requests` → Rate limiting (wait 10-15 minutes)
- `502/503` → Temporary GitHub service issue (check [githubstatus.com](https://www.githubstatus.com))

---

## Prevention Tips

### Keep Everything Updated
- **Enable auto-updates:** File → Preferences → Settings → Search "update mode" → Set to "default"
- **Check for updates weekly:** Help → Check for Updates
- **Update extensions monthly:** Extensions panel → Click gear icon → "Auto Update"

### Workspace Configuration
This project includes recommended VS Code settings in `.vscode/settings.json` and `.vscode/extensions.json` to ensure optimal Copilot compatibility.

**Recommended settings:**
```json
{
  "github.copilot.enable": {
    "*": true,
    "markdown": true,
    "plaintext": false
  },
  "github.copilot.advanced": {
    "debug.overrideEngine": "",
    "debug.testOverrideProxyUrl": "",
    "authProvider": "github"
  }
}
```

---

## Still Not Working?

### Check GitHub Service Status
- Visit [githubstatus.com](https://www.githubstatus.com)
- Look for incidents affecting GitHub Copilot
- Check [@githubstatus](https://twitter.com/githubstatus) on Twitter/X

### Contact GitHub Support
If none of the above steps work:

1. **GitHub Copilot Support:**
   - Visit [support.github.com](https://support.github.com)
   - Select "Copilot" as the product
   - Include error details, request ID, and troubleshooting steps tried

2. **VS Code GitHub Issues:**
   - Search [github.com/microsoft/vscode/issues](https://github.com/microsoft/vscode/issues)
   - File a new issue if none match your problem
   - Tag with `github-copilot` label

3. **Community Forums:**
   - [GitHub Community Discussions](https://github.com/orgs/community/discussions/categories/copilot)
   - [VS Code Subreddit](https://reddit.com/r/vscode)
   - [Stack Overflow](https://stackoverflow.com/questions/tagged/github-copilot)

---

## For SICO GRC Project Developers

### Project-Specific Copilot Configuration
This repository includes:
- **`.github/copilot-instructions.md`:** Custom instructions for Copilot to understand SICO architecture
- **`.vscode/settings.json`:** Recommended workspace settings
- **`.vscode/extensions.json`:** Recommended extensions including latest Copilot

### Bilingual Development Context
Copilot in this project should understand:
- **Arabic/English bilingual support** (i18n patterns)
- **Saudi regulatory frameworks** (ECC, CCC, PDPL)
- **FastAPI backend + Next.js 14 frontend** architecture
- **LangChain RAG implementation** patterns

If Copilot suggestions seem unaware of these contexts, ensure you're using the latest version and that the `.github/copilot-instructions.md` file is present.

---

## Version History

| Date       | Version | Changes                                    |
|------------|---------|-------------------------------------------|
| 2026-02-11 | 1.0     | Initial troubleshooting guide created     |

---

## References

- [Official GitHub Copilot Troubleshooting](https://docs.github.com/en/copilot/troubleshooting-github-copilot)
- [VS Code Copilot Extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [VS Code Issue #294296](https://github.com/microsoft/vscode/issues/294296) - API version error discussion
