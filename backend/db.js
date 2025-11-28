import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

dotenv.config();

// Get database configuration from environment
// Support both DB_* and MYSQL_* variable names for flexibility
const dbConfig = {
  host: process.env.MYSQL_HOST || process.env.DB_HOST || 'localhost',
  user: process.env.MYSQL_USER || process.env.DB_USER || 'root',
  password: process.env.MYSQL_PASSWORD || process.env.DB_PASSWORD || '',
  database: process.env.MYSQL_DATABASE || process.env.DB_NAME || 'neuromate web',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
};

// Validate configuration
if (!dbConfig.password && dbConfig.user === 'root') {
  console.warn('⚠️  Warning: No password set for MySQL root user.');
  console.warn('   If MySQL requires a password, set MYSQL_PASSWORD in backend/.env file');
}

// Create connection pool
export const db = mysql.createPool(dbConfig);

// Test connection with better error handling
db.getConnection()
  .then(connection => {
    console.log('✅ Connected to MySQL database');
    connection.release();
  })
  .catch(err => {
    console.error('❌ Database connection error:', err.message);
    if (err.code === 'ER_ACCESS_DENIED_ERROR') {
      console.error('\n💡 Solution:');
      console.error('   1. Check your MySQL username and password in backend/.env');
      console.error('   2. Make sure MySQL is running');
      console.error('   3. Verify MYSQL_USER and MYSQL_PASSWORD in backend/.env');
      console.error('   4. Test connection: mysql -u root -p');
    } else if (err.code === 'ECONNREFUSED') {
      console.error('\n💡 Solution:');
      console.error('   1. Make sure MySQL server is running');
      console.error('   2. Check DB_HOST in backend/.env (default: localhost)');
    } else if (err.code === 'ER_BAD_DB_ERROR') {
      console.error('\n💡 Solution:');
      console.error('   1. Create the database: CREATE DATABASE neuromate;');
      console.error('   2. Or update DB_NAME in backend/.env');
    }
    process.exit(1);
  });

export default db;

