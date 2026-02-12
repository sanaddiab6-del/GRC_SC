# GitHub Codespaces Quick Start Guide

## 🚀 Launching Your Codespace

GitHub Codespaces provides a complete development environment in your browser. This guide will help you get started with the SICO GRC Platform.

---

## Option 1: Launch from GitHub.com (Recommended)

1. **Navigate to the repository**: https://github.com/sonaiso/sanadcom

2. **Click the green "Code" button** at the top right

3. **Select the "Codespaces" tab**

4. **Click "Create codespace on [branch-name]"**
   - For the latest stable code, use `main`
   - For development work, use your feature branch

5. **Wait for initialization** (5-15 minutes first time)
   - The Codespace will build the container
   - Install Python and Node.js dependencies
   - Start database services
   - Run database migrations

6. **Look for "✅ Setup complete!"** in the terminal

---

## Option 2: Launch from VS Code Desktop

1. **Install prerequisites**:
   - Visual Studio Code Desktop
   - GitHub Codespaces extension

2. **Open Command Palette** (Ctrl/Cmd + Shift + P)

3. **Type**: `Codespaces: Create New Codespace`

4. **Select**: `sonaiso/sanadcom`

5. **Choose your branch**

6. **Wait for initialization** (same as Option 1)

---

## After Launch: Starting the Application

Once you see "✅ Setup complete!", you need to start the backend and frontend:

### Start Backend API

Open a terminal and run:
```bash
cd src/backend
uvicorn main:app --reload --host 0.0.0.0
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Start Frontend (New Terminal)

Open a **new terminal** (click the `+` button) and run:
```bash
cd src/frontend
npm run dev
```

Expected output:
```
> sico-frontend@0.1.0 dev
> next dev

- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled successfully
```

---

## Accessing Your Application

### View Forwarded Ports

1. **Click on the "Ports" tab** in the terminal panel
2. You'll see all forwarded ports with their URLs

### Open the Application

Click on the globe icon next to:
- **Port 3000**: Frontend UI
- **Port 8000**: Backend API
- **Port 8000/docs**: Interactive API documentation

Or hover over the port number and click "Open in Browser"

---

## Codespace Stuck Loading? Try These Solutions

### Solution 1: Wait Longer (Most Common)
- **First-time setup can take 10-15 minutes**
- Check the "Creation Log" for progress
- Look for network/download activity

### Solution 2: Check Creation Log
1. If stuck on "Setting up your codespace..."
2. Click "View Creation Log" link
3. Look for errors in the output
4. Common issues:
   - Network timeouts → Retry
   - Docker build failures → Check Dockerfile
   - Permission errors → Contact repository owner

### Solution 3: Rebuild the Container
1. Open Command Palette (Ctrl/Cmd + Shift + P)
2. Type: `Codespaces: Rebuild Container`
3. Select "Rebuild Container"
4. Wait for rebuild to complete

### Solution 4: Delete and Recreate
1. Go to https://github.com/codespaces
2. Find your stuck Codespace
3. Click the "..." menu → Delete
4. Return to the repository and create a new Codespace

### Solution 5: Check GitHub Status
- Visit: https://www.githubstatus.com/
- Look for Codespaces service issues
- If there's an incident, wait for resolution

### Solution 6: Try a Different Machine Type
1. When creating Codespace, click "Configure and create codespace"
2. Select a larger machine type (4-core or 8-core)
3. Create the Codespace

---

## Troubleshooting Common Issues

### Issue: "Port already in use"

**Solution:**
```bash
# Find the process
lsof -i :8000  # or :3000

# Kill it
kill -9 <PID>
```

### Issue: "Cannot connect to database"

**Solution:**
```bash
# Check Docker services
cd deployment
docker-compose ps

# Restart services if needed
docker-compose down
docker-compose up -d postgres redis chroma

# View logs
docker-compose logs -f postgres
```

### Issue: "Module not found" errors

**Solution:**
```bash
# Reinstall backend dependencies
cd src/backend
pip install -r requirements.txt

# Reinstall frontend dependencies
cd src/frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Frontend shows "API connection failed"

**Solutions:**
1. Ensure backend is running on port 8000
2. Check `.env` file exists with correct settings
3. Verify port forwarding is working (Ports tab)
4. Try accessing http://localhost:8000/health directly

### Issue: Database migration errors

**Solution:**
```bash
cd src/backend

# Check database connection
python -c "from core.database import engine; print('✅ Connected')"

# Run migrations
alembic upgrade head

# If still failing, reset database
cd ../../deployment
docker-compose down -v  # WARNING: Deletes all data
docker-compose up -d postgres
cd ../src/backend
alembic upgrade head
```

---

## Performance Tips

1. **Choose the right machine size**:
   - 2-core: Documentation only
   - 4-core: Normal development ✅ (Recommended)
   - 8-core: Heavy workloads (AI training, large builds)

2. **Keep Codespace alive**:
   - Settings → Codespaces → Default idle timeout
   - Set to 30+ minutes

3. **Use Prebuilds** (Repository admin only):
   - Significantly speeds up Codespace creation
   - Settings → Codespaces → Prebuilds → Set up prebuild

4. **Stop when not in use**:
   - Codespaces → Your codespace → Stop
   - Saves billing hours

---

## What Happens During Setup?

The `.devcontainer/setup.sh` script automatically:

1. ✅ Installs Python 3.11 dependencies (~5 min)
2. ✅ Installs Node.js 20 dependencies (~3 min)
3. ✅ Creates `.env` configuration file
4. ✅ Starts Docker services:
   - PostgreSQL (database)
   - Redis (cache)
   - Chroma (vector database)
5. ✅ Waits for PostgreSQL to be ready
6. ✅ Runs database migrations (Alembic)
7. ✅ Displays success message with next steps

**Total time**: 10-15 minutes first time, 2-3 minutes after prebuild

---

## Codespace vs Local Development

| Feature | Codespace | Local Development |
|---------|-----------|-------------------|
| Setup time | 10-15 min (first time) | 30-60 min |
| Dependencies | Pre-installed | Manual install |
| Docker required | No (built-in) | Yes |
| Resource usage | GitHub's servers | Your computer |
| Access | Any device with browser | Specific machine |
| Cost | Free tier available | Free (uses your hardware) |

---

## Need Help?

1. **Check the logs**:
   - Terminal output during setup
   - Docker logs: `docker-compose logs -f`
   - Backend logs: Check terminal running uvicorn
   - Frontend logs: Check terminal running npm

2. **Review documentation**:
   - [.devcontainer/README.md](.devcontainer/README.md)
   - [QUICK_START.md](QUICK_START.md)
   - [README.md](README.md)

3. **Common resources**:
   - [GitHub Codespaces Docs](https://docs.github.com/en/codespaces)
   - [Dev Container Specification](https://containers.dev/)

4. **Still stuck?**
   - Open an issue with:
     - Codespace creation log
     - Terminal output
     - Error messages
     - Steps you've tried

---

## Next Steps

Once your Codespace is running:

1. **Explore the codebase**:
   - `src/backend/` - FastAPI backend
   - `src/frontend/` - Next.js frontend
   - `data/` - Control libraries
   - `ai/` - RAG engine

2. **Run tests**:
   ```bash
   cd src/backend && pytest tests/ -v
   cd src/frontend && npm test
   ```

3. **Try the demo**:
   ```bash
   bash start-demo.sh
   ```

4. **Read the architecture docs**:
   - [docs/architecture/README.md](docs/architecture/README.md)

5. **Start developing**:
   - Create a new branch
   - Make your changes
   - Commit and push
   - Open a pull request

---

**Happy coding! 🚀**
