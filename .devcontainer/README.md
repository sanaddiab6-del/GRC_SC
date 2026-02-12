# GitHub Codespaces Configuration

This directory contains the configuration for GitHub Codespaces.

## ⚡ Quick Start (Updated for Faster Launch)

### What Changed?
The Codespace now launches **immediately** without waiting for all dependencies to install. Setup runs in the background so you can start coding right away!

## What's Included

### devcontainer.json
The main configuration file that tells Codespaces:
- What base Docker image to use (Python 3.11)
- What features to install (Docker, Git, GitHub CLI, Node.js)
- What VS Code extensions to install
- Which ports to forward
- **NEW:** Non-blocking setup (UI available in <2 minutes)

### Setup Scripts

1. **setup-background.sh** (Automatic)
   - Runs automatically in the background when Codespace starts
   - Installs dependencies without blocking the UI
   - Log file: `/tmp/setup.log`
   - Check progress: `tail -f /tmp/setup.log`

2. **quick-start.sh** (Manual - Fast)
   - Minimal setup for immediate development
   - Installs only essential packages (~2 minutes)
   - Run: `bash .devcontainer/quick-start.sh`

3. **setup.sh** (Manual - Complete)
   - Full setup including AI/ML dependencies
   - Run when you need all features
   - Run: `bash .devcontainer/setup.sh`

## How to Use

### Starting a Codespace

1. **From GitHub.com:**
   - Go to the repository: https://github.com/sonaiso/sanadcom
   - Click the green "Code" button
   - Select "Codespaces" tab
   - Click "Create codespace on main" (or your branch)

2. **From VS Code:**
   - Install the "GitHub Codespaces" extension
   - Open Command Palette (Ctrl/Cmd + Shift + P)
   - Type "Codespaces: Create New Codespace"
   - Select the repository

### After Launch (< 2 minutes)

Your Codespace UI will be available immediately! Background setup is running.

**Check setup progress:**
```bash
tail -f /tmp/setup.log
```

**Quick start (if you can't wait):**
```bash
bash .devcontainer/quick-start.sh
```

**Full setup (when you need everything):**
```bash
bash .devcontainer/setup.sh
```

### Starting the Application

Once setup is complete, you need to start the backend and frontend manually:

**Backend API:**
```bash
cd src/backend
uvicorn main:app --reload --host 0.0.0.0
```

**Frontend (in a new terminal):**
```bash
cd src/frontend
npm run dev
```

### Accessing the Application

The following ports are automatically forwarded:
- **Port 3000**: Frontend (Next.js)
- **Port 8000**: Backend API (FastAPI)
- **Port 5432**: PostgreSQL
- **Port 6379**: Redis
- **Port 8001**: Chroma Vector DB

Click on the "Ports" tab in VS Code to see the URLs.

## Troubleshooting

### Codespace is stuck loading

If your Codespace gets stuck during creation:
1. Wait at least 10-15 minutes (initial setup can be slow)
2. Check the creation log for errors
3. Try deleting and recreating the Codespace
4. Check if there are any GitHub service issues

### Services not starting

If Docker services don't start:
```bash
cd deployment
docker-compose up -d
docker-compose logs -f
```

### Dependencies not installed

If you need to reinstall dependencies:
```bash
# Backend
cd src/backend
pip install -r requirements.txt

# Frontend
cd src/frontend
npm install
```

### Database connection issues

Check if PostgreSQL is running:
```bash
cd deployment
docker-compose ps
docker-compose logs postgres
```

### Port already in use

If you get "port already in use" errors:
```bash
# Find the process using the port
lsof -i :8000  # or :3000, :5432, etc.

# Kill the process
kill -9 <PID>
```

## Rebuilding the Container

If you make changes to `.devcontainer/devcontainer.json`:
1. Open Command Palette (Ctrl/Cmd + Shift + P)
2. Type "Codespaces: Rebuild Container"
3. Wait for the rebuild to complete

## Customization

### Adding VS Code Extensions

Edit `devcontainer.json` and add extension IDs to the `extensions` array:
```json
"extensions": [
  "ms-python.python",
  "your-extension-id"
]
```

### Changing Port Forwarding

Edit `devcontainer.json` and modify the `forwardPorts` array:
```json
"forwardPorts": [3000, 8000, 5432],
```

### Modifying Setup Script

Edit `setup.sh` to add or remove initialization steps.

## Performance Tips

1. **Codespace size**: Use at least 4-core/8GB machine for this project
2. **Keep Codespace alive**: Set timeout to 30 minutes or more in settings
3. **Prebuild**: Enable prebuilds in repository settings for faster startup
4. **Docker**: Services run in Docker, so ensure Docker is healthy

## Resources

- [Codespaces Documentation](https://docs.github.com/en/codespaces)
- [Dev Container Specification](https://containers.dev/)
- [Project Quick Start](../QUICK_START.md)
- [Project README](../README.md)

## Support

If you continue to experience issues:
1. Check the terminal output for errors
2. Review the setup log
3. Try rebuilding the container
4. Delete and recreate the Codespace
5. Report the issue with error logs
