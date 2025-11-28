import express from 'express';
import { v4 as uuidv4 } from 'uuid';
import { db } from '../db.js';

const router = express.Router();

// Beta signup (public endpoint, no auth required)
router.post('/signup', async (req, res) => {
  try {
    const { name, email, phone } = req.body;

    if (!name || !email || !phone) {
      return res.status(400).json({ error: 'Name, email, and phone are required' });
    }

    const id = uuidv4();

    await db.execute(
      'INSERT INTO beta_signups (id, name, email, phone) VALUES (?, ?, ?, ?)',
      [id, name.trim(), email.trim(), phone.trim()]
    );

    res.status(201).json({ 
      message: 'Beta signup successful',
      id 
    });
  } catch (error) {
    console.error('Beta signup error:', error);
    res.status(500).json({ error: 'Failed to process beta signup' });
  }
});

export default router;

