-- Seed Script for NeuroMate Database
-- This script populates the database with sample data for testing
-- Usage: mysql -u root -p "neuromate web" < seed_data.sql

-- First, get a test user ID (you may need to adjust this based on actual users)
-- For now, we'll use a sample UUID that you can replace with an actual user ID

-- Sample user ID (replace with actual user ID from your database)
-- Run this query first to get your user ID:
-- SELECT id FROM users LIMIT 1;

-- For demonstration, we'll use a placeholder UUID
-- You need to update USER_ID_HERE with an actual user ID from your database

SET @user_id = (SELECT id FROM users LIMIT 1);

-- If no users exist, create a test user
IF @user_id IS NULL THEN
  INSERT INTO users (id, email, password_hash) 
  VALUES ('550e8400-e29b-41d4-a716-446655440000', 'demo@neuromate.com', '$2a$10$N9qo8uLOickgx2ZMRZoMye');
  
  SET @user_id = '550e8400-e29b-41d4-a716-446655440000';
  
  INSERT INTO profiles (id, email, username) 
  VALUES (@user_id, 'demo@neuromate.com', 'demouser');
END IF;

-- Insert sample tasks (completed and pending)
INSERT INTO tasks (user_id, title, description, completed, completed_at, created_at) VALUES
(@user_id, 'Complete project report', 'Finish the Q4 project report', TRUE, DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),
(@user_id, 'Review team feedback', 'Go through team member reviews and feedback', TRUE, DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY)),
(@user_id, 'Schedule 1:1 meetings', 'Book one-on-one meetings with team leads', TRUE, DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),
(@user_id, 'Prepare presentation', 'Create slides for the upcoming conference', FALSE, NULL, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(@user_id, 'Update documentation', 'Update API documentation for new endpoints', FALSE, NULL, DATE_SUB(NOW(), INTERVAL 1 DAY)),
(@user_id, 'Code review pull requests', 'Review pending PRs from team members', FALSE, NULL, NOW());

-- Insert sample mood checkins (distributed over past 30 days)
INSERT INTO mood_checkins (user_id, mood_level, mood_type, notes, created_at) VALUES
(@user_id, 5, 'happy', 'Had a great productive day!', DATE_SUB(NOW(), INTERVAL 7 DAY)),
(@user_id, 4, 'content', 'Feeling good about progress', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(@user_id, 3, 'neutral', 'Just another day', DATE_SUB(NOW(), INTERVAL 5 DAY)),
(@user_id, 5, 'excited', 'Completed a big milestone!', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(@user_id, 4, 'calm', 'Nice relaxing evening', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(@user_id, 5, 'happy', 'Great day with team', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(@user_id, 4, 'content', 'Satisfied with progress', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(@user_id, 5, 'happy', 'Feeling energized today!', NOW()),
(@user_id, 3, 'tired', 'Long day at work', DATE_SUB(NOW(), INTERVAL 8 DAY)),
(@user_id, 2, 'stressed', 'Facing challenges', DATE_SUB(NOW(), INTERVAL 9 DAY)),
(@user_id, 4, 'determined', 'Ready for challenges', DATE_SUB(NOW(), INTERVAL 10 DAY)),
(@user_id, 5, 'grateful', 'Thankful for support', DATE_SUB(NOW(), INTERVAL 11 DAY));

-- Insert sample focus sessions
INSERT INTO focus_sessions (user_id, activity, duration_minutes, notes, started_at, created_at) VALUES
(@user_id, 'Deep work - coding', 120, 'Completed feature implementation', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),
(@user_id, 'Writing documentation', 90, 'Updated API docs', DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 6 DAY)),
(@user_id, 'Code review', 60, 'Reviewed 3 pull requests', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),
(@user_id, 'Meeting preparation', 45, 'Prepared slides and notes', DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY)),
(@user_id, 'Bug fixing', 100, 'Fixed critical production bug', DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),
(@user_id, 'Planning sprint', 75, 'Planned next sprint tasks', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY)),
(@user_id, 'Learning new tech', 80, 'Studied React hooks', DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),
(@user_id, 'Project architecture', 110, 'Designed new system architecture', NOW(), NOW());

-- Insert sample journal entries
INSERT INTO journal_entries (user_id, title, content, mood, created_at) VALUES
(@user_id, 'Productive Monday', 'Had an amazing start to the week. Completed the feature that was blocking other work. Team collaboration went smoothly.', 'happy', DATE_SUB(NOW(), INTERVAL 10 DAY)),
(@user_id, 'Overcoming challenges', 'Faced some technical challenges today but managed to solve them with the help of the team. Learned a lot in the process.', 'determined', DATE_SUB(NOW(), INTERVAL 8 DAY)),
(@user_id, 'Reflection on growth', 'Looking back at the past month, I can see how much I have improved. My problem-solving skills are stronger now.', 'grateful', DATE_SUB(NOW(), INTERVAL 5 DAY)),
(@user_id, 'Work-life balance', 'Managed to balance work with personal time today. Felt refreshed and energized for upcoming tasks.', 'content', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(@user_id, 'Celebrating wins', 'Our team successfully launched the new feature! So proud of what we accomplished together. Great day overall.', 'excited', DATE_SUB(NOW(), INTERVAL 1 DAY));

-- Insert sample routines
INSERT INTO routines (user_id, name, description, completed, completed_at, created_at) VALUES
(@user_id, 'Morning meditation', '10 minutes of guided meditation', TRUE, DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 30 DAY)),
(@user_id, 'Exercise routine', '30 minutes of workout (running/gym)', TRUE, DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 30 DAY)),
(@user_id, 'Evening reflection', '5 minutes journaling before bed', TRUE, DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 30 DAY)),
(@user_id, 'Healthy breakfast', 'Eat a nutritious breakfast', TRUE, NOW(), DATE_SUB(NOW(), INTERVAL 30 DAY)),
(@user_id, 'Read for 30 mins', 'Read a book or technical article', FALSE, NULL, DATE_SUB(NOW(), INTERVAL 30 DAY));

-- Insert sample meditation sessions
INSERT INTO meditation_sessions (user_id, type, duration_minutes, notes, started_at, created_at) VALUES
(@user_id, 'Mindfulness', 10, 'Morning meditation', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),
(@user_id, 'Breathing exercises', 8, 'Calm breathing technique', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),
(@user_id, 'Guided meditation', 15, 'Sleep preparation meditation', DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),
(@user_id, 'Body scan', 12, 'Progressive muscle relaxation', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY)),
(@user_id, 'Mindfulness', 10, 'Evening meditation', DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),
(@user_id, 'Visualization', 20, 'Guided visualization session', NOW(), NOW());

-- Insert sample community posts
INSERT INTO posts (user_id, content, created_at) VALUES
(@user_id, 'Just completed my first week of consistent meditation! Feeling amazing.', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(@user_id, 'Sharing my productivity tips: Break work into 90-minute focused sessions with short breaks.', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(@user_id, 'Mental health matters! Remember to take care of yourself today.', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(@user_id, 'Celebrating a big win with the team! Hard work pays off. 🎉', DATE_SUB(NOW(), INTERVAL 1 DAY));

-- Insert sample post comments
INSERT INTO post_comments (post_id, user_id, content, created_at)
SELECT id, @user_id, 'Great post! This really helped me.', DATE_SUB(NOW(), INTERVAL 5 DAY)
FROM posts WHERE user_id = @user_id AND content LIKE '%meditation%'
LIMIT 1;

-- Display summary of inserted data
SELECT 'Data seeding completed!' AS status;
SELECT CONCAT('User ID: ', @user_id) AS info;
SELECT CONCAT('Tasks inserted: ', COUNT(*)) AS data FROM tasks WHERE user_id = @user_id;
SELECT CONCAT('Mood checkins inserted: ', COUNT(*)) AS data FROM mood_checkins WHERE user_id = @user_id;
SELECT CONCAT('Focus sessions inserted: ', COUNT(*)) AS data FROM focus_sessions WHERE user_id = @user_id;
SELECT CONCAT('Journal entries inserted: ', COUNT(*)) AS data FROM journal_entries WHERE user_id = @user_id;
SELECT CONCAT('Routines inserted: ', COUNT(*)) AS data FROM routines WHERE user_id = @user_id;
SELECT CONCAT('Meditation sessions inserted: ', COUNT(*)) AS data FROM meditation_sessions WHERE user_id = @user_id;
