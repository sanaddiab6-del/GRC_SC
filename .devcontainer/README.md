# GitHub Codespaces Configuration

This directory contains the configuration for GitHub Codespaces.

## ⚡ SIMPLIFIED APPROACH (Best Practice)

**Key Change:** No automated setup that could fail or block the UI.

Following GitHub Codespaces best practices:
- ✅ Minimal container configuration
- ✅ Fast, predictable startup
- ✅ Manual setup with clear instructions
- ✅ No background processes
- ✅ No blocking operations

## What's Included

### devcontainer.json
Minimal configuration that:
- Uses Python 3.11 base image
- Installs Docker, Git, GitHub CLI, Node.js 20
- Configures VS Code extensions
- Sets up port forwarding
- **Runs only simple version check on creation**

### Setup Scripts (Run Manually)

1. **show-welcome.sh**
   - Displays welcome message with instructions
   - Run: `bash .devcontainer/show-welcome.sh`

2. **quick-start.sh**
   - Minimal setup for immediate development (2-3 min)
   - Installs only essential packages
   - Run: `bash .devcontainer/quick-start.sh`

3. **setup.sh**
   - Full setup including AI/ML dependencies (10-15 min)
   - Run when you need all features
   - Run: `bash .devcontainer/setup.sh`

## How to Use

### Starting a Codespace

1. **From GitHub.com:**
   - Go to: https://github.com/sonaiso/sanadcom
   - Click "Code" → "Codespaces" → "Create codespace"

2. **From VS Code:**
   - Open Command Palette (Ctrl/Cmd + Shift + P)
   - Type "Codespaces: Create New Codespace"
   - Select the repository

### After Launch (30-60 seconds)

Your Codespace UI will be available immediately!

**See welcome message:**
```bash
bash .devcontainer/show-welcome.sh
```

**Quick setup (2-3 min):**
```bash
bash .devcontainer/quick-start.sh
```

**Full setup (10-15 min):**
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
