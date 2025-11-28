#!/usr/bin/env node

/**
 * NeuroMate Database Seeding Script
 * 
 * Usage:
 *   node seed.js
 * 
 * This script populates the database with sample data for testing
 * the activity calendar and dashboard features.
 */

import mysql from 'mysql2/promise';
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

// Get the directory of this file
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load .env from backend directory
dotenv.config({ path: resolve(__dirname, '../backend/.env') });

const dbConfig = {
  host: process.env.MYSQL_HOST || 'localhost',
  user: process.env.MYSQL_USER || 'root',
  password: process.env.MYSQL_PASSWORD || '',
  database: process.env.MYSQL_DATABASE || 'neuromate web',
};

const SAMPLE_DATA = {
  tasks: [
    { title: 'Complete project report', description: 'Finish the Q4 project report', daysAgo: 5, completedDaysAgo: 3 },
    { title: 'Review team feedback', description: 'Go through team member reviews and feedback', daysAgo: 4, completedDaysAgo: 2 },
    { title: 'Schedule 1:1 meetings', description: 'Book one-on-one meetings with team leads', daysAgo: 3, completedDaysAgo: 1 },
    { title: 'Prepare presentation', description: 'Create slides for the upcoming conference', daysAgo: 2, completedDaysAgo: null },
    { title: 'Update documentation', description: 'Update API documentation for new endpoints', daysAgo: 1, completedDaysAgo: null },
    { title: 'Code review pull requests', description: 'Review pending PRs from team members', daysAgo: 0, completedDaysAgo: null },
  ],
  moods: [
    { level: 5, type: 'happy', notes: 'Had a great productive day!', daysAgo: 7 },
    { level: 4, type: 'content', notes: 'Feeling good about progress', daysAgo: 6 },
    { level: 3, type: 'neutral', notes: 'Just another day', daysAgo: 5 },
    { level: 5, type: 'excited', notes: 'Completed a big milestone!', daysAgo: 4 },
    { level: 4, type: 'calm', notes: 'Nice relaxing evening', daysAgo: 3 },
    { level: 5, type: 'happy', notes: 'Great day with team', daysAgo: 2 },
    { level: 4, type: 'content', notes: 'Satisfied with progress', daysAgo: 1 },
    { level: 5, type: 'happy', notes: 'Feeling energized today!', daysAgo: 0 },
    { level: 3, type: 'tired', notes: 'Long day at work', daysAgo: 8 },
    { level: 2, type: 'stressed', notes: 'Facing challenges', daysAgo: 9 },
    { level: 4, type: 'determined', notes: 'Ready for challenges', daysAgo: 10 },
    { level: 5, type: 'grateful', notes: 'Thankful for support', daysAgo: 11 },
  ],
  focusSessions: [
    { activity: 'Deep work - coding', duration: 120, notes: 'Completed feature implementation', daysAgo: 7 },
    { activity: 'Writing documentation', duration: 90, notes: 'Updated API docs', daysAgo: 6 },
    { activity: 'Code review', duration: 60, notes: 'Reviewed 3 pull requests', daysAgo: 5 },
    { activity: 'Meeting preparation', duration: 45, notes: 'Prepared slides and notes', daysAgo: 4 },
    { activity: 'Bug fixing', duration: 100, notes: 'Fixed critical production bug', daysAgo: 3 },
    { activity: 'Planning sprint', duration: 75, notes: 'Planned next sprint tasks', daysAgo: 2 },
    { activity: 'Learning new tech', duration: 80, notes: 'Studied React hooks', daysAgo: 1 },
    { activity: 'Project architecture', duration: 110, notes: 'Designed new system architecture', daysAgo: 0 },
  ],
  journals: [
    { title: 'Productive Monday', content: 'Had an amazing start to the week. Completed the feature that was blocking other work. Team collaboration went smoothly.', mood: 'happy', daysAgo: 10 },
    { title: 'Overcoming challenges', content: 'Faced some technical challenges today but managed to solve them with the help of the team. Learned a lot in the process.', mood: 'determined', daysAgo: 8 },
    { title: 'Reflection on growth', content: 'Looking back at the past month, I can see how much I have improved. My problem-solving skills are stronger now.', mood: 'grateful', daysAgo: 5 },
    { title: 'Work-life balance', content: 'Managed to balance work with personal time today. Felt refreshed and energized for upcoming tasks.', mood: 'content', daysAgo: 3 },
    { title: 'Celebrating wins', content: 'Our team successfully launched the new feature! So proud of what we accomplished together. Great day overall.', mood: 'excited', daysAgo: 1 },
  ],
  routines: [
    { name: 'Morning meditation', description: '10 minutes of guided meditation', isCompleted: true },
    { name: 'Exercise routine', description: '30 minutes of workout (running/gym)', isCompleted: true },
    { name: 'Evening reflection', description: '5 minutes journaling before bed', isCompleted: true },
    { name: 'Healthy breakfast', description: 'Eat a nutritious breakfast', isCompleted: true },
    { name: 'Read for 30 mins', description: 'Read a book or technical article', isCompleted: false },
  ],
  meditations: [
    { type: 'Mindfulness', duration: 10, notes: 'Morning meditation', daysAgo: 7 },
    { type: 'Breathing exercises', duration: 8, notes: 'Calm breathing technique', daysAgo: 5 },
    { type: 'Guided meditation', duration: 15, notes: 'Sleep preparation meditation', daysAgo: 3 },
    { type: 'Body scan', duration: 12, notes: 'Progressive muscle relaxation', daysAgo: 2 },
    { type: 'Mindfulness', duration: 10, notes: 'Evening meditation', daysAgo: 1 },
    { type: 'Visualization', duration: 20, notes: 'Guided visualization session', daysAgo: 0 },
  ],
  posts: [
    { content: 'Just completed my first week of consistent meditation! Feeling amazing.', daysAgo: 6 },
    { content: 'Sharing my productivity tips: Break work into 90-minute focused sessions with short breaks.', daysAgo: 4 },
    { content: 'Mental health matters! Remember to take care of yourself today.', daysAgo: 2 },
    { content: 'Celebrating a big win with the team! Hard work pays off. 🎉', daysAgo: 1 },
  ],
};

function getDateSubtract(daysAgo) {
  const date = new Date();
  date.setDate(date.getDate() - daysAgo);
  return date;
}

async function seedDatabase() {
  let connection;

  try {
    console.log('🌱 Starting database seeding...\n');

    // Connect to database
    connection = await mysql.createConnection(dbConfig);
    console.log('✅ Connected to database\n');

    // Get or create test user
    const [users] = await connection.execute('SELECT id FROM users LIMIT 1');
    let userId;

    if (users.length > 0) {
      userId = users[0].id;
      console.log(`✅ Using existing user: ${userId}\n`);
    } else {
      userId = uuidv4();
      console.log(`📝 Creating test user: ${userId}`);
      
      await connection.execute(
        'INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)',
        [userId, 'demo@neuromate.com', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcatt7v21dY3P3RgFziDlH2']
      );

      await connection.execute(
        'INSERT INTO profiles (id, email, username) VALUES (?, ?, ?)',
        [userId, 'demo@neuromate.com', 'demouser']
      );
      console.log('✅ Test user created\n');
    }

    // Seed tasks
    console.log('📝 Seeding tasks...');
    for (const task of SAMPLE_DATA.tasks) {
      const createdAt = getDateSubtract(task.daysAgo);
      const completedAt = task.completedDaysAgo !== null ? getDateSubtract(task.completedDaysAgo) : null;

      await connection.execute(
        'INSERT INTO tasks (user_id, title, description, completed, completed_at, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        [userId, task.title, task.description, completedAt !== null, completedAt, createdAt]
      );
    }
    console.log(`✅ Created ${SAMPLE_DATA.tasks.length} tasks\n`);

    // Seed mood checkins
    console.log('📝 Seeding mood checkins...');
    for (const mood of SAMPLE_DATA.moods) {
      const createdAt = getDateSubtract(mood.daysAgo);
      await connection.execute(
        'INSERT INTO mood_checkins (user_id, mood_level, mood_type, notes, created_at) VALUES (?, ?, ?, ?, ?)',
        [userId, mood.level, mood.type, mood.notes, createdAt]
      );
    }
    console.log(`✅ Created ${SAMPLE_DATA.moods.length} mood checkins\n`);

    // Seed focus sessions
    console.log('📝 Seeding focus sessions...');
    for (const session of SAMPLE_DATA.focusSessions) {
      const startedAt = getDateSubtract(session.daysAgo);
      await connection.execute(
        'INSERT INTO focus_sessions (user_id, activity, duration_minutes, notes, started_at, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        [userId, session.activity, session.duration, session.notes, startedAt, startedAt]
      );
    }
    console.log(`✅ Created ${SAMPLE_DATA.focusSessions.length} focus sessions\n`);

    // Seed journal entries
    console.log('📝 Seeding journal entries...');
    for (const journal of SAMPLE_DATA.journals) {
      const createdAt = getDateSubtract(journal.daysAgo);
      await connection.execute(
        'INSERT INTO journal_entries (user_id, title, content, mood, created_at) VALUES (?, ?, ?, ?, ?)',
        [userId, journal.title, journal.content, journal.mood, createdAt]
      );
    }
    console.log(`✅ Created ${SAMPLE_DATA.journals.length} journal entries\n`);

    // Seed routines
    console.log('📝 Seeding routines...');
    for (const routine of SAMPLE_DATA.routines) {
      const completedAt = routine.isCompleted ? getDateSubtract(0) : null;
      await connection.execute(
        'INSERT INTO routines (user_id, name, description, completed, completed_at, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        [userId, routine.name, routine.description, routine.isCompleted, completedAt, getDateSubtract(30)]
      );
    }
    console.log(`✅ Created ${SAMPLE_DATA.routines.length} routines\n`);

    // Seed meditation sessions
    console.log('📝 Seeding meditation sessions...');
    for (const meditation of SAMPLE_DATA.meditations) {
      const startedAt = getDateSubtract(meditation.daysAgo);
      await connection.execute(
        'INSERT INTO meditation_sessions (user_id, type, duration_minutes, notes, started_at, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        [userId, meditation.type, meditation.duration, meditation.notes, startedAt, startedAt]
      );
    }
    console.log(`✅ Created ${SAMPLE_DATA.meditations.length} meditation sessions\n`);

    // Seed community posts (skip if table doesn't exist)
    console.log('📝 Seeding community posts...');
    try {
      for (const post of SAMPLE_DATA.posts) {
        const createdAt = getDateSubtract(post.daysAgo);
        await connection.execute(
          'INSERT INTO posts (user_id, content, created_at) VALUES (?, ?, ?)',
          [userId, post.content, createdAt]
        );
      }
      console.log(`✅ Created ${SAMPLE_DATA.posts.length} community posts\n`);
    } catch (error) {
      if (error.code === 'ER_NO_SUCH_TABLE') {
        console.log('⚠️  Posts table not found. Skipping community posts.\n');
      } else {
        throw error;
      }
    }

    // Print summary
    console.log('🎉 Database seeding completed successfully!\n');
    console.log('📊 Summary:');
    console.log(`   User ID: ${userId}`);
    console.log(`   Tasks: ${SAMPLE_DATA.tasks.length}`);
    console.log(`   Mood Checkins: ${SAMPLE_DATA.moods.length}`);
    console.log(`   Focus Sessions: ${SAMPLE_DATA.focusSessions.length}`);
    console.log(`   Journal Entries: ${SAMPLE_DATA.journals.length}`);
    console.log(`   Routines: ${SAMPLE_DATA.routines.length}`);
    console.log(`   Meditation Sessions: ${SAMPLE_DATA.meditations.length}`);
    console.log(`   Community Posts: ${SAMPLE_DATA.posts.length}`);
    console.log('\n💡 Tip: Use this user ID to test the activity calendar on the dashboard!\n');

    await connection.end();
  } catch (error) {
    console.error('❌ Error seeding database:', error);
    process.exit(1);
  }
}

seedDatabase();
