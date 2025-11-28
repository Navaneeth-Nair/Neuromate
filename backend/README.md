# NeuroMate Backend API

Express.js backend server for NeuroMate with MySQL database.

## Setup Instructions

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# MySQL Configuration
USE_MYSQL=true
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=neuromate web

# Server Configuration
PORT=3001
NODE_ENV=development

# JWT Secret (generate a strong random string)
JWT_SECRET=your_jwt_secret_key_here
JWT_EXPIRES_IN=7d
```

**Note:** The code also supports `DB_*` variable names for backward compatibility.

### 3. MySQL Setup

#### Example Configuration
```env
USE_MYSQL=true
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=neuromate web
```

#### Option: Create a new MySQL user (Recommended for production)
```sql
CREATE USER 'neuromate'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON `neuromate web`.* TO 'neuromate'@'localhost';
FLUSH PRIVILEGES;
```

Then in `.env`:
```env
MYSQL_USER=neuromate
MYSQL_PASSWORD=your_password
```

### 4. Create Database

```sql
CREATE DATABASE `neuromate web` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Run Migrations

```bash
mysql -u root -proot "neuromate web" < ../mysql/migrations/001_initial_schema.sql
```

Or if using a different password:
```bash
mysql -u root -p "neuromate web" < ../mysql/migrations/001_initial_schema.sql
```

### 6. Start Server

Development mode (with auto-reload):
```bash
npm run dev
```

Production mode:
```bash
npm start
```

The API will be available at `http://localhost:3001`

## Troubleshooting

### Access Denied Error
- Check your MySQL username and password in `.env`
- Make sure MySQL server is running
- Try connecting manually: `mysql -u root -p`

### Database Not Found
- Create the database: `CREATE DATABASE \`neuromate web\`;`
- Run the migration script

### Connection Refused
- Make sure MySQL server is running
- Check if MySQL is listening on the correct port (default: 3306)

