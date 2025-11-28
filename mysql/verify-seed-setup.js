#!/usr/bin/env node

/**
 * NeuroMate Pre-Seed Verification Script
 * 
 * Checks if the environment is ready for database seeding
 * Run this before seed.js to ensure everything is configured correctly
 * 
 * Usage: node verify-seed-setup.js
 */

import mysql from 'mysql2/promise';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
dotenv.config({ path: path.join(__dirname, '../backend/.env') });

const dbConfig = {
  host: process.env.MYSQL_HOST || 'localhost',
  user: process.env.MYSQL_USER || 'root',
  password: process.env.MYSQL_PASSWORD || '',
  database: process.env.MYSQL_DATABASE || 'neuromate web',
};

const checks = {
  passed: 0,
  failed: 0,
  warnings: 0,
};

function log(message, type = 'info') {
  const icons = {
    info: 'ℹ️ ',
    success: '✅ ',
    error: '❌ ',
    warning: '⚠️ ',
    title: '🔍 ',
  };
  console.log(`${icons[type] || '→ '} ${message}`);
}

function section(title) {
  console.log('\n' + '━'.repeat(60));
  log(title, 'title');
  console.log('━'.repeat(60));
}

async function checkEnvFile() {
  section('Environment Configuration');
  
  const envPath = path.join(__dirname, '../backend/.env');
  
  if (!fs.existsSync(envPath)) {
    log('No .env file found at backend/.env', 'error');
    log('Create a .env file in backend/ with the following:');
    console.log(`
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=neuromate web
JWT_SECRET=your_secret_key
    `);
    checks.failed++;
    return false;
  }
  
  log('.env file exists', 'success');
  checks.passed++;
  
  log(`Database Host: ${dbConfig.host}`, 'info');
  log(`Database User: ${dbConfig.user}`, 'info');
  log(`Database Name: ${dbConfig.database}`, 'info');
  
  return true;
}

async function checkMysqlConnection() {
  section('MySQL Connection');
  
  try {
    const connection = await mysql.createConnection(dbConfig);
    log('Connected to MySQL successfully', 'success');
    checks.passed++;
    
    // Check database exists
    const [databases] = await connection.execute(
      'SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = ?',
      [dbConfig.database]
    );
    
    if (databases.length === 0) {
      log(`Database "${dbConfig.database}" not found`, 'error');
      checks.failed++;
      await connection.end();
      return false;
    }
    
    log(`Database "${dbConfig.database}" exists`, 'success');
    checks.passed++;
    
    // Check required tables
    const requiredTables = [
      'users',
      'profiles',
      'tasks',
      'mood_checkins',
      'focus_sessions',
      'journal_entries',
      'routines',
      'meditation_sessions',
      'posts',
    ];
    
    const [tables] = await connection.execute(
      'SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = ?',
      [dbConfig.database]
    );
    
    const existingTables = tables.map(t => t.TABLE_NAME);
    const missingTables = requiredTables.filter(t => !existingTables.includes(t));
    
    if (missingTables.length > 0) {
      log(`Missing tables: ${missingTables.join(', ')}`, 'error');
      log('Run database migrations first:', 'warning');
      log('  mysql -u root -p "neuromate web" < mysql/migrations/001_initial_schema.sql', 'info');
      checks.failed++;
      await connection.end();
      return false;
    }
    
    log(`All required tables exist (${requiredTables.length} tables)`, 'success');
    checks.passed++;
    
    await connection.end();
    return true;
  } catch (error) {
    log(`Connection failed: ${error.message}`, 'error');
    log('Make sure MySQL is running and credentials are correct', 'warning');
    checks.failed++;
    return false;
  }
}

async function checkNodeDependencies() {
  section('Node.js Dependencies');
  
  const backendPath = path.join(__dirname, '../backend/node_modules');
  
  if (!fs.existsSync(backendPath)) {
    log('node_modules not found in backend/', 'warning');
    log('Run: npm install in backend/ directory', 'info');
    checks.warnings++;
    return false;
  }
  
  const requiredModules = ['mysql2', 'uuid', 'dotenv'];
  let allFound = true;
  
  for (const module of requiredModules) {
    const modulePath = path.join(backendPath, module);
    if (fs.existsSync(modulePath)) {
      log(`${module} installed`, 'success');
      checks.passed++;
    } else {
      log(`${module} not found`, 'error');
      checks.failed++;
      allFound = false;
    }
  }
  
  return allFound;
}

async function checkSeedFiles() {
  section('Seed Script Files');
  
  const files = ['seed.js', 'seed_data.sql', 'SEEDING_GUIDE.md'];
  
  for (const file of files) {
    const filePath = path.join(__dirname, file);
    if (fs.existsSync(filePath)) {
      const stats = fs.statSync(filePath);
      log(`${file} exists (${stats.size} bytes)`, 'success');
      checks.passed++;
    } else {
      log(`${file} not found`, 'error');
      checks.failed++;
    }
  }
}

function summary() {
  section('Verification Summary');
  
  console.log(`✅ Passed: ${checks.passed}`);
  if (checks.warnings > 0) console.log(`⚠️  Warnings: ${checks.warnings}`);
  if (checks.failed > 0) console.log(`❌ Failed: ${checks.failed}`);
  
  const total = checks.passed + checks.failed;
  const percentage = total > 0 ? Math.round((checks.passed / total) * 100) : 0;
  
  console.log(`\nStatus: ${percentage}% ready\n`);
  
  if (checks.failed === 0) {
    log('✨ Everything looks good! Ready to seed the database.', 'success');
    console.log('\nRun: node seed.js\n');
    return true;
  } else {
    log('⚠️  Please fix the issues above before seeding.', 'warning');
    console.log();
    return false;
  }
}

async function main() {
  console.clear();
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║    NeuroMate Database Seeding - Environment Verification    ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');
  
  try {
    await checkEnvFile();
    await checkMysqlConnection();
    await checkNodeDependencies();
    await checkSeedFiles();
    const ready = summary();
    
    process.exit(ready ? 0 : 1);
  } catch (error) {
    log(`Unexpected error: ${error.message}`, 'error');
    process.exit(1);
  }
}

main();
