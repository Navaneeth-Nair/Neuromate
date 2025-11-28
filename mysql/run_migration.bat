@echo off
REM MySQL Migration Script Runner for Windows
REM This script helps run the migration even if MySQL is not in PATH

echo Checking for MySQL...

REM Check common MySQL locations
if exist "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" (
    set MYSQL_PATH=C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe
    goto :found
)
if exist "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" (
    set MYSQL_PATH=C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe
    goto :found
)
if exist "C:\xampp\mysql\bin\mysql.exe" (
    set MYSQL_PATH=C:\xampp\mysql\bin\mysql.exe
    goto :found
)
if exist "C:\wamp64\bin\mysql\mysql8.0\bin\mysql.exe" (
    set MYSQL_PATH=C:\wamp64\bin\mysql\mysql8.0\bin\mysql.exe
    goto :found
)

echo.
echo MySQL not found in common locations.
echo Please either:
echo 1. Add MySQL to your PATH, OR
echo 2. Edit this script and set MYSQL_PATH to your MySQL installation
echo.
pause
exit /b 1

:found
echo Found MySQL at: %MYSQL_PATH%
echo.
echo Running migration for database "neuromate web"...
echo.

"%MYSQL_PATH%" -u root -proot "neuromate web" < "%~dp0\001_initial_schema.sql"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Migration completed successfully!
) else (
    echo.
    echo ❌ Migration failed. Check the error messages above.
)

pause

