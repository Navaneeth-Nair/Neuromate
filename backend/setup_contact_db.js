import { db } from './db.js';

async function setupDatabase() {
    try {
        console.log('Initializing Contact and Beta tables...');

        // Create contact_messages table
        await db.execute(`
      CREATE TABLE IF NOT EXISTS contact_messages (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
        console.log('✅ contact_messages table created or already exists');

        // Create beta_signups table
        await db.execute(`
      CREATE TABLE IF NOT EXISTS beta_signups (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        phone VARCHAR(50) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
        console.log('✅ beta_signups table created or already exists');

        console.log('Database setup completed successfully.');
        process.exit(0);
    } catch (error) {
        console.error('❌ Database setup failed:', error);
        process.exit(1);
    }
}

setupDatabase();
