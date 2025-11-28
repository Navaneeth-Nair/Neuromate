# Manual MySQL Migration Guide

If MySQL is not in your PATH, use one of these methods:

## Method 1: Use Full Path to MySQL

Find your MySQL installation and use the full path:

### For MySQL Server (Standalone):
```cmd
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -proot "neuromate web" < mysql\migrations\001_initial_schema.sql
```

### For XAMPP:
```cmd
C:\xampp\mysql\bin\mysql.exe -u root -proot "neuromate web" < mysql\migrations\001_initial_schema.sql
```

### For WAMP:
```cmd
C:\wamp64\bin\mysql\mysql8.0\bin\mysql.exe -u root -proot "neuromate web" < mysql\migrations\001_initial_schema.sql
```

## Method 2: Add MySQL to PATH

1. Find your MySQL installation directory (usually `C:\Program Files\MySQL\MySQL Server 8.0\bin`)
2. Add it to Windows PATH:
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Go to "Advanced" tab → "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add your MySQL bin directory
   - Click OK on all dialogs
3. Restart your terminal/command prompt
4. Run: `mysql -u root -proot "neuromate web" < mysql\migrations\001_initial_schema.sql`

## Method 3: Use MySQL Workbench or phpMyAdmin

1. Open MySQL Workbench or phpMyAdmin
2. Connect to your MySQL server
3. Create the database:
   ```sql
   CREATE DATABASE `neuromate web` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
4. Select the database
5. Copy and paste the contents of `mysql/migrations/001_initial_schema.sql` into the SQL editor
6. Execute the script

## Method 4: Use the Batch Script

Run the provided `run_migration.bat` script in the `mysql/` directory. It will try to find MySQL automatically.

