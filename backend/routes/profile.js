import express from 'express';
import { db } from '../db.js';
import { verifyToken } from './auth.js';

const router = express.Router();

// Get profile
router.get('/', verifyToken, async (req, res) => {
  try {
    const [profiles] = await db.execute(
      'SELECT * FROM profiles WHERE id = ?',
      [req.userId]
    );

    if (profiles.length === 0) {
      return res.status(404).json({ error: 'Profile not found' });
    }

    res.json(profiles[0]);
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({ error: 'Failed to fetch profile' });
  }
});

// Update profile
router.put('/', verifyToken, async (req, res) => {
  try {
    const updates = req.body;
    const allowedFields = ['username', 'avatar_url', 'mood', 'status', 'first_name', 'last_name', 'phone_number'];
    const fieldsToUpdate = {};

    for (const field of allowedFields) {
      if (updates[field] !== undefined) {
        fieldsToUpdate[field] = updates[field];
      }
    }

    if (Object.keys(fieldsToUpdate).length === 0) {
      return res.status(400).json({ error: 'No valid fields to update' });
    }

    // Log avatar update (but don't log the full base64 data)
    if (fieldsToUpdate.avatar_url) {
      const avatarSize = fieldsToUpdate.avatar_url.length;
      console.log(`Updating avatar for user ${req.userId}: ${avatarSize} bytes`);
      
      // Check if avatar is too large
      if (avatarSize > 16777215) { // 16MB limit for LONGTEXT
        return res.status(400).json({ error: 'Avatar image is too large. Maximum 16MB allowed.' });
      }
    }

    const setClause = Object.keys(fieldsToUpdate).map(key => `${key} = ?`).join(', ');
    const values = [...Object.values(fieldsToUpdate), req.userId];

    console.log('Executing update query:', `UPDATE profiles SET ${setClause} WHERE id = ?`, 'with values:', values);

    const result = await db.execute(
      `UPDATE profiles SET ${setClause} WHERE id = ?`,
      values
    );

    if (result[0].affectedRows === 0) {
      console.log('No profile found for user:', req.userId);
      return res.status(404).json({ error: 'Profile not found' });
    }

    // Fetch and return updated profile
    const [profiles] = await db.execute(
      'SELECT * FROM profiles WHERE id = ?',
      [req.userId]
    );

    if (profiles.length === 0) {
      return res.status(404).json({ error: 'Profile not found' });
    }

    return res.json(profiles[0]);
  } catch (error) {
    console.error('Update profile error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Failed to update profile';
    return res.status(500).json({ error: errorMessage });
  }
});

export default router;

