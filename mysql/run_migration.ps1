# PowerShell script to run MySQL migration
# Usage: .\run_migration.ps1

$mysqlPath = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
$scriptPath = Join-Path $PSScriptRoot "001_initial_schema.sql"
$database = "neuromate web"
$user = "root"
$password = "root"

Write-Host "Running MySQL migration for database: $database" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $mysqlPath)) {
    Write-Host "❌ MySQL not found at: $mysqlPath" -ForegroundColor Red
    Write-Host "Please update the mysqlPath variable in this script" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found MySQL at: $mysqlPath" -ForegroundColor Green
Write-Host ""

try {
    Get-Content $scriptPath | & $mysqlPath -u $user -p$password $database
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Migration completed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Migration failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "❌ Error running migration: $_" -ForegroundColor Red
    exit 1
}

