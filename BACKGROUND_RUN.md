# Running NeuroMate in the Background

This guide explains how to run the NeuroMate frontend and backend servers in the background on Windows.

## Quick Start

### Option 1: PowerShell Scripts (Recommended)

1. **Start servers in background:**
   ```powershell
   .\start_background.ps1
   ```

2. **Stop servers:**
   ```powershell
   .\stop_background.ps1
   ```

### Option 2: Batch Scripts

1. **Start servers in background:**
   ```cmd
   start_background.bat
   ```

2. **Stop servers:**
   ```cmd
   stop_background.bat
   ```

## What Happens When You Start

When you run `start_background.ps1` or `start_background.bat`:

1. **Backend server** starts on port **3001** in a minimized window
2. **Frontend server** starts on port **8080** in a minimized window
3. Both servers run in the background

### Access Points

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:3001
- **Backend Health Check**: http://localhost:3001/health

## Manual Background Process (Alternative)

If you prefer to run them manually in separate terminal windows:

### Backend
```bash
cd backend
npm run dev
```

### Frontend (in a new terminal)
```bash
npm run dev
```

## Prerequisites

Before running the servers:

1. ✅ **Install dependencies:**
   ```bash
   npm install
   cd backend
   npm install
   cd ..
   ```

2. ✅ **Set up MySQL database:**
   - Create database: `CREATE DATABASE \`neuromate web\`;`
   - Run migration: See `mysql/run_migration.ps1` or `mysql/run_migration.bat`

3. ✅ **Configure backend environment:**
   - Create `backend/.env` file (see `backend/README.md` for template)
   - Required variables:
     ```
     MYSQL_HOST=localhost
     MYSQL_USER=root
     MYSQL_PASSWORD=root
     MYSQL_DATABASE=neuromate web
     PORT=3001
     JWT_SECRET=your_secret_key_here
     ```

## Troubleshooting

### Servers won't start
- Check if ports 3001 and 8080 are already in use
- Verify MySQL is running
- Check that `backend/.env` file exists and is configured correctly

### Can't stop servers
- Run `stop_background.ps1` or `stop_background.bat`
- If that doesn't work, manually close the minimized windows
- As last resort: `taskkill /F /IM node.exe /T` (stops all Node.js processes)

### Permission errors (PowerShell)
If you get execution policy errors, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Notes

- The PowerShell scripts track process IDs in `.server_pids` file for easier stopping
- The batch scripts open minimized windows you can manually close
- Both methods run servers in development mode with hot-reload enabled
- To run in production mode, use `npm start` instead of `npm run dev`

