import express from 'express';
import { v4 as uuidv4 } from 'uuid';
import { db } from '../db.js';

const router = express.Router();

// Send contact message (public endpoint)
router.post('/', async (req, res) => {
    try {
        const { name, email, message } = req.body;

        if (!name || !email || !message) {
            return res.status(400).json({ error: 'Name, email, and message are required' });
        }

        const id = uuidv4();

        await db.execute(
            'INSERT INTO contact_messages (id, name, email, message) VALUES (?, ?, ?, ?)',
            [id, name.trim(), email.trim(), message.trim()]
        );

        res.status(201).json({
            message: 'Message sent successfully',
            id
        });
    } catch (error) {
        console.error('Contact message error:', error);
        res.status(500).json({ error: 'Failed to send message' });
    }
});

export default router;
