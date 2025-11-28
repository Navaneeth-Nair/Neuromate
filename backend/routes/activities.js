import express from 'express';
import { v4 as uuidv4 } from 'uuid';
import { db } from '../db.js';
import { verifyToken } from './auth.js';

const router = express.Router();

// Get all activities for a user
router.get('/', verifyToken, async (req, res) => {
  try {
    const { type, startDate, endDate } = req.query;
    const userId = req.userId;

    let query = '';
    let params = [userId];

    switch (type) {
      case 'tasks':
        query = 'SELECT * FROM tasks WHERE user_id = ?';
        if (startDate) {
          query += ' AND created_at >= ?';
          params.push(startDate);
        }
        if (endDate) {
          query += ' AND created_at <= ?';
          params.push(endDate);
        }
        query += ' ORDER BY created_at DESC';
        break;
      case 'moods':
        query = 'SELECT * FROM mood_checkins WHERE user_id = ?';
        if (startDate) {
          query += ' AND created_at >= ?';
          params.push(startDate);
        }
        if (endDate) {
          query += ' AND created_at <= ?';
          params.push(endDate);
        }
        query += ' ORDER BY created_at DESC';
        break;
      case 'focus':
        query = 'SELECT * FROM focus_sessions WHERE user_id = ?';
        if (startDate) {
          query += ' AND started_at >= ?';
          params.push(startDate);
        }
        if (endDate) {
          query += ' AND started_at <= ?';
          params.push(endDate);
        }
        query += ' ORDER BY started_at DESC';
        break;
      case 'journals':
        query = 'SELECT * FROM journal_entries WHERE user_id = ?';
        if (startDate) {
          query += ' AND created_at >= ?';
          params.push(startDate);
        }
        if (endDate) {
          query += ' AND created_at <= ?';
          params.push(endDate);
        }
        query += ' ORDER BY created_at DESC';
        break;
      case 'routines':
        query = 'SELECT * FROM routines WHERE user_id = ?';
        if (startDate) {
          query += ' AND created_at >= ?';
          params.push(startDate);
        }
        if (endDate) {
          query += ' AND created_at <= ?';
          params.push(endDate);
        }
        query += ' ORDER BY created_at DESC';
        break;
      case 'meditations':
        query = 'SELECT * FROM meditation_sessions WHERE user_id = ?';
        if (startDate) {
          query += ' AND started_at >= ?';
          params.push(startDate);
        }
        if (endDate) {
          query += ' AND started_at <= ?';
          params.push(endDate);
        }
        query += ' ORDER BY started_at DESC';
        break;
      case 'posts':
        // Fetch all posts, not just user's, for community feed? 
        // Usually community feed is global.
        // But for now let's just fetch all posts.
        query = 'SELECT * FROM posts ORDER BY created_at DESC';
        params = []; // No user_id filter for global feed
        break;
      case 'my-posts':
        query = 'SELECT * FROM posts WHERE user_id = ? ORDER BY created_at DESC';
        // params already contains userId from initialization
        break;
      default:
        return res.status(400).json({ error: 'Invalid activity type' });
    }

    const [results] = await db.execute(query, params);
    res.json(results);
  } catch (error) {
    console.error('Get activities error:', error);
    res.status(500).json({ error: 'Failed to fetch activities' });
  }
});

// Create task
router.post('/tasks', verifyToken, async (req, res) => {
  try {
    const { title, description, completed } = req.body;
    const id = uuidv4();
    const completedAt = completed ? new Date().toISOString().slice(0, 19).replace('T', ' ') : null;

    await db.execute(
      'INSERT INTO tasks (id, user_id, title, description, completed, completed_at) VALUES (?, ?, ?, ?, ?, ?)',
      [id, req.userId, title, description || null, completed || false, completedAt]
    );

    const [tasks] = await db.execute('SELECT * FROM tasks WHERE id = ?', [id]);
    res.status(201).json(tasks[0]);
  } catch (error) {
    console.error('Create task error:', error);
    res.status(500).json({ error: 'Failed to create task' });
  }
});

// Create mood checkin
router.post('/moods', verifyToken, async (req, res) => {
  try {
    const { mood_level, mood_type, notes } = req.body;
    const id = uuidv4();

    await db.execute(
      'INSERT INTO mood_checkins (id, user_id, mood_level, mood_type, notes) VALUES (?, ?, ?, ?, ?)',
      [id, req.userId, mood_level, mood_type, notes]
    );

    const [moods] = await db.execute('SELECT * FROM mood_checkins WHERE id = ?', [id]);
    res.status(201).json(moods[0]);
  } catch (error) {
    console.error('Create mood error:', error);
    res.status(500).json({ error: 'Failed to create mood checkin' });
  }
});

// Create focus session
router.post('/focus', verifyToken, async (req, res) => {
  try {
    const { activity, duration_minutes, notes } = req.body;
    const id = uuidv4();

    await db.execute(
      'INSERT INTO focus_sessions (id, user_id, activity, duration_minutes, notes) VALUES (?, ?, ?, ?, ?)',
      [id, req.userId, activity, duration_minutes, notes]
    );

    const [sessions] = await db.execute('SELECT * FROM focus_sessions WHERE id = ?', [id]);
    res.status(201).json(sessions[0]);
  } catch (error) {
    console.error('Create focus session error:', error);
    res.status(500).json({ error: 'Failed to create focus session' });
  }
});

// Create journal entry
router.post('/journals', verifyToken, async (req, res) => {
  try {
    const { title, content, mood } = req.body;
    const id = uuidv4();

    await db.execute(
      'INSERT INTO journal_entries (id, user_id, title, content, mood) VALUES (?, ?, ?, ?, ?)',
      [id, req.userId, title, content, mood]
    );

    const [entries] = await db.execute('SELECT * FROM journal_entries WHERE id = ?', [id]);
    res.status(201).json(entries[0]);
  } catch (error) {
    console.error('Create journal error:', error);
    res.status(500).json({ error: 'Failed to create journal entry' });
  }
});

// Create routine
router.post('/routines', verifyToken, async (req, res) => {
  try {
    const { name, description, completed } = req.body;
    const id = uuidv4();
    const completedAt = completed ? new Date().toISOString().slice(0, 19).replace('T', ' ') : null;

    await db.execute(
      'INSERT INTO routines (id, user_id, name, description, completed, completed_at) VALUES (?, ?, ?, ?, ?, ?)',
      [id, req.userId, name, description || null, completed || false, completedAt]
    );

    const [routines] = await db.execute('SELECT * FROM routines WHERE id = ?', [id]);
    res.status(201).json(routines[0]);
  } catch (error) {
    console.error('Create routine error:', error);
    res.status(500).json({ error: 'Failed to create routine' });
  }
});

// Create meditation session
router.post('/meditations', verifyToken, async (req, res) => {
  try {
    const { type, duration_minutes, notes } = req.body;
    const id = uuidv4();

    await db.execute(
      'INSERT INTO meditation_sessions (id, user_id, type, duration_minutes, notes) VALUES (?, ?, ?, ?, ?)',
      [id, req.userId, type, duration_minutes, notes]
    );

    const [sessions] = await db.execute('SELECT * FROM meditation_sessions WHERE id = ?', [id]);
    res.status(201).json(sessions[0]);
  } catch (error) {
    console.error('Create meditation error:', error);
    res.status(500).json({ error: 'Failed to create meditation session' });
  }
});

// Create community post
router.post('/posts', verifyToken, async (req, res) => {
  try {
    const { content } = req.body;
    const id = uuidv4();

    await db.execute(
      'INSERT INTO posts (id, user_id, content) VALUES (?, ?, ?)',
      [id, req.userId, content]
    );

    const [posts] = await db.execute('SELECT * FROM posts WHERE id = ?', [id]);
    res.status(201).json(posts[0]);
  } catch (error) {
    console.error('Create post error:', error);
    res.status(500).json({ error: 'Failed to create post' });
  }
});

export default router;

