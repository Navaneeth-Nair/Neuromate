# NeuroMate AI - Project Overview

## 📋 Project Summary

**NeuroMate** is a full-stack AI-powered mental health companion application that helps users track their mental wellness, manage tasks, log moods, and connect with a community. The project has recently migrated from Supabase to MySQL for the backend.

**Project URL:** https://lovable.dev/projects/97da1721-ba18-4187-8ce6-cebbbd545527

---

## 🏗️ Tech Stack

### Frontend
- **Framework:** React 18.3.1 with TypeScript
- **Build Tool:** Vite
- **UI Library:** shadcn/ui (Radix UI components)
- **Styling:** Tailwind CSS
- **State Management:** TanStack React Query (for server state)
- **Routing:** React Router v6
- **Forms:** React Hook Form
- **Icons:** Lucide React
- **Charts:** Recharts

### Backend
- **Runtime:** Node.js
- **Framework:** Express.js
- **Database:** MySQL (database name: `neuromate web`)
- **Authentication:** JWT (JSON Web Tokens)
- **Password Hashing:** bcryptjs
- **ORM:** mysql2/promise
- **Environment:** dotenv

---

## 📂 Project Structure

```
neuromate-ai-07-main/
├── src/                                 # Frontend source code
│   ├── pages/                          # React page components
│   │   ├── Home.tsx
│   │   ├── Auth.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Profile.tsx
│   │   ├── Settings.tsx
│   │   ├── Community.tsx
│   │   ├── Productivity.tsx
│   │   ├── About.tsx
│   │   ├── Features.tsx
│   │   ├── Download.tsx
│   │   ├── Contact.tsx
│   │   ├── Pricing.tsx
│   │   ├── CustomizeAvatar.tsx
│   │   ├── KillSwitch.tsx
│   │   └── NotFound.tsx
│   │
│   ├── components/
│   │   ├── Layout.tsx
│   │   ├── Navbar.tsx
│   │   ├── Footer.tsx
│   │   ├── ContributionCalendar.tsx
│   │   ├── FeatureCard.tsx
│   │   ├── PersonalSectionPanel.tsx
│   │   ├── activities/                 # Activity-related components
│   │   │   ├── AddActivityDialog.tsx
│   │   │   ├── AddTaskForm.tsx
│   │   │   ├── AddMoodForm.tsx
│   │   │   ├── AddFocusSessionForm.tsx
│   │   │   ├── AddJournalForm.tsx
│   │   │   ├── AddRoutineForm.tsx
│   │   │   └── AddMeditationForm.tsx
│   │   ├── community/                  # Community features
│   │   │   ├── CommunityLeftSidebar.tsx
│   │   │   ├── CommunityMainFeed.tsx
│   │   │   ├── CommunityRightSidebar.tsx
│   │   │   ├── CreatePostBox.tsx
│   │   │   └── PostCard.tsx
│   │   └── ui/                         # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── dialog.tsx
│   │       ├── input.tsx
│   │       ├── form.tsx
│   │       ├── chart.tsx
│   │       └── ... (40+ UI components)
│   │
│   ├── hooks/
│   │   ├── useAuth.tsx                # Authentication hook
│   │   ├── useProfile.tsx             # User profile hook
│   │   ├── useActivityData.tsx        # Activity data hook
│   │   ├── useTheme.tsx               # Theme management
│   │   ├── use-mobile.tsx
│   │   └── use-toast.ts
│   │
│   ├── lib/
│   │   ├── api.ts                     # API client with all endpoints
│   │   └── utils.ts                   # Utility functions
│   │
│   ├── App.tsx                        # Main app component
│   ├── main.tsx
│   ├── vite-env.d.ts
│   └── index.css
│
├── backend/                            # Node.js/Express backend
│   ├── server.js                      # Express server setup
│   ├── db.js                          # MySQL connection pool
│   ├── package.json
│   ├── .env                           # Environment variables (create this)
│   ├── README.md                      # Backend setup guide
│   └── routes/
│       ├── auth.js                    # Authentication endpoints
│       ├── profile.js                 # User profile endpoints
│       ├── activities.js              # Activity endpoints
│       └── beta.js                    # Beta signup endpoint
│
├── mysql/                              # Database migration files
│   ├── migrations/
│   │   └── 001_initial_schema.sql    # Database schema
│   ├── create_database.sql
│   ├── verify_tables.sql
│   ├── run_migration.bat              # Windows batch script
│   ├── run_migration.ps1              # PowerShell script
│   └── run_migration_manual.md
│
├── public/                             # Static assets
│   └── robots.txt
│
├── Configuration Files
│   ├── package.json                   # Frontend dependencies
│   ├── vite.config.ts                 # Vite configuration
│   ├── tsconfig.json                  # TypeScript config
│   ├── tailwind.config.ts             # Tailwind configuration
│   ├── postcss.config.js              # PostCSS configuration
│   ├── eslint.config.js               # ESLint configuration
│   ├── components.json                # shadcn/ui configuration
│   └── bun.lockb                      # Bun lock file
│
├── Documentation
│   ├── README.md                      # Main project readme
│   ├── MIGRATION_GUIDE.md             # Supabase to MySQL migration guide
│   ├── MIGRATION_COMPLETE.md          # Migration completion status
│   ├── BACKGROUND_RUN.md              # How to run servers in background
│   └── .env.example                   # Environment variables template
│
└── index.html                          # HTML entry point
```

---

## 🔐 Authentication Flow

1. **User Registration/Login** → Sent to `POST /api/auth/signup` or `POST /api/auth/signin`
2. **Backend** → Validates credentials, hashes password, creates JWT token
3. **Token Storage** → JWT token stored in `localStorage` as `auth_token`
4. **Authenticated Requests** → All API calls include `Authorization: Bearer {token}` header
5. **Token Validation** → Backend validates token and returns user data

### Auth Endpoints (backend/routes/auth.js)
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Login user
- `PUT /api/auth/password` - Change password
- `GET /api/auth/profile` - Get current user profile (requires auth)

---

## 📊 Database Schema

### Core Tables
1. **users** - User accounts
   - `id` (UUID primary key)
   - `email` (unique)
   - `password_hash`
   - `email_verified`
   - `created_at`, `updated_at`

2. **profiles** - User profiles
   - `id` (references users.id)
   - `username`, `email`
   - `avatar_url`
   - `mood`, `status`
   - `first_name`, `last_name`, `phone_number`
   - `created_at`, `updated_at`

3. **user_roles** - Role assignments
   - `id` (UUID)
   - `user_id`
   - `role` (admin, moderator, user)

### Activity Tables
4. **tasks** - User tasks
   - `id`, `user_id`
   - `title`, `description`
   - `completed`, `completed_at`
   - `created_at`, `updated_at`

5. **mood_checkins** - Mood tracking
   - `id`, `user_id`
   - `mood_level` (1-5)
   - `mood_type`
   - `notes`
   - `created_at`

6. **focus_sessions** - Focus time tracking
   - `id`, `user_id`
   - `activity`, `duration_minutes`
   - `notes`
   - `started_at`

7. **journal_entries** - Journal logs
   - `id`, `user_id`
   - `title`, `content`
   - `mood`, `created_at`

8. **routines** - Daily routines
   - `id`, `user_id`
   - `name`, `description`
   - `completed`, `created_at`

9. **meditation_sessions** - Meditation tracking
   - `id`, `user_id`
   - `type`, `duration_minutes`
   - `notes`, `started_at`

### Community Tables
10. **posts** - Community posts
    - `id`, `user_id`
    - `content`, `created_at`

11. **post_comments** - Post comments
    - `id`, `post_id`, `user_id`
    - `content`, `created_at`

### Other Tables
12. **beta_signups** - Beta program signups
    - `id`, `name`, `email`, `phone`, `created_at`

13. **app_roles** - Available roles
    - `role_name` (admin, moderator, user)

---

## 🔌 API Endpoints

### Authentication (`/api/auth`)
- `POST /signup` - Register user
- `POST /signin` - Login user
- `PUT /password` - Change password
- `GET /profile` - Get user profile

### Profile (`/api/profile`)
- `GET /` - Get current user profile
- `PUT /` - Update user profile
- `POST /avatar` - Upload avatar (base64)

### Activities (`/api/activities`)
- **Tasks:**
  - `GET /tasks` - Get all tasks
  - `POST /tasks` - Create task
  - `PUT /tasks/:id` - Update task
  - `DELETE /tasks/:id` - Delete task

- **Moods:**
  - `GET /moods` - Get all moods
  - `POST /moods` - Create mood checkin
  - `DELETE /moods/:id` - Delete mood

- **Focus Sessions:**
  - `GET /focus` - Get all focus sessions
  - `POST /focus` - Create focus session
  - `DELETE /focus/:id` - Delete session

- **Journals:**
  - `GET /journals` - Get all journal entries
  - `POST /journals` - Create journal entry
  - `DELETE /journals/:id` - Delete entry

- **Routines:**
  - `GET /routines` - Get all routines
  - `POST /routines` - Create routine
  - `PUT /routines/:id` - Update routine
  - `DELETE /routines/:id` - Delete routine

- **Meditations:**
  - `GET /meditations` - Get all meditation sessions
  - `POST /meditations` - Create meditation session
  - `DELETE /meditations/:id` - Delete session

### Beta (`/api/beta`)
- `POST /signup` - Sign up for beta program

---

## 🚀 Setup & Installation

### Prerequisites
- Node.js (v16+)
- npm or bun
- MySQL server (8.0+)

### Step 1: Install Dependencies

**Frontend:**
```bash
npm install
# or
bun install
```

**Backend:**
```bash
cd backend
npm install
```

### Step 2: Set Up MySQL Database

```bash
# Create database
CREATE DATABASE `neuromate web` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Run migration
cd mysql
# Windows batch:
run_migration.bat
# OR PowerShell:
run_migration.ps1
# OR manually:
mysql -u root -p "neuromate web" < migrations/001_initial_schema.sql
```

### Step 3: Configure Environment Variables

**Backend** (`backend/.env`):
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=neuromate web
PORT=3001
NODE_ENV=development
JWT_SECRET=your_jwt_secret_key_here
JWT_EXPIRES_IN=7d
```

**Frontend** (`.env`):
```env
VITE_API_URL=http://localhost:3001/api
```

### Step 4: Start Servers

**Backend** (Terminal 1):
```bash
cd backend
npm run dev
# API will run on http://localhost:3001
```

**Frontend** (Terminal 2):
```bash
npm run dev
# Frontend will run on http://localhost:8080
```

### Alternative: Run in Background

**Windows PowerShell:**
```bash
.\start_background.ps1
```

**Windows Command Prompt:**
```bash
start_background.bat
```

See `BACKGROUND_RUN.md` for more details.

---

## 📁 Key Files to Understand

### Frontend Architecture
- **`src/App.tsx`** - Main app with route configuration
- **`src/lib/api.ts`** - Central API client, all endpoints defined here
- **`src/hooks/useAuth.tsx`** - Authentication state management
- **`src/hooks/useProfile.tsx`** - User profile state management
- **`src/hooks/useActivityData.tsx`** - Activity data state management

### Backend Architecture
- **`backend/server.js`** - Express app setup and routes registration
- **`backend/db.js`** - MySQL connection pool configuration
- **`backend/routes/auth.js`** - Authentication logic (signup, signin, JWT)
- **`backend/routes/profile.js`** - Profile management endpoints
- **`backend/routes/activities.js`** - All activity CRUD operations
- **`backend/routes/beta.js`** - Beta signup endpoint

### Configuration
- **`vite.config.ts`** - Vite build configuration
- **`tsconfig.json`** - TypeScript compiler options
- **`tailwind.config.ts`** - Tailwind CSS customization
- **`components.json`** - shadcn/ui configuration

---

## 🔄 Recent Migration

The project was recently migrated from **Supabase** to **MySQL**. The following was changed:

✅ **Completed:**
- Database migrated from PostgreSQL to MySQL
- Authentication switched from Supabase Auth to JWT
- User hooks updated to use new API
- All components updated to use backend API
- Avatar upload now uses base64 encoding
- Removed all Supabase dependencies

⚠️ **Important:**
- MySQL database name: `neuromate web` (with space)
- Ensure backend `.env` is configured before starting
- Run database migrations before first use

---

## 🛠️ Development Workflow

### Adding a New Feature

1. **Backend:**
   - Add endpoint in appropriate `backend/routes/` file
   - Update `/api/activities` or `/api/profile` as needed
   - Test with Postman/curl

2. **Frontend:**
   - Add API function to `src/lib/api.ts`
   - Create/update hook in `src/hooks/`
   - Create component in `src/components/`
   - Add page/route in `src/pages/`
   - Update `src/App.tsx` routes if needed

### Running in Development Mode

**With hot-reload (recommended):**
```bash
# Terminal 1 - Backend
cd backend && npm run dev

# Terminal 2 - Frontend
npm run dev
```

### Building for Production

```bash
# Build frontend
npm run build

# Deploy backend separately to hosting
cd backend
npm install --production
npm start
```

---

## 📝 Available Pages

| Page | Route | Description |
|------|-------|-------------|
| Home | `/` | Landing page |
| About | `/about` | About the project |
| Features | `/features` | Feature showcase |
| Download | `/download` | Download app |
| Pricing | `/pricing` | Pricing information |
| Contact | `/contact` | Contact & beta signup |
| Auth | `/auth` | Login/Register |
| Dashboard | `/dashboard` | Main dashboard |
| Profile | `/profile` | User profile |
| Settings | `/settings` | User settings |
| Community | `/community/*` | Community feed |
| Productivity | `/productivity` | Productivity tracking |
| Customize Avatar | `/customize-avatar` | Avatar customization |
| Kill Switch | `/kill-switch` | Kill switch page |
| 404 | `*` | Not found page |

---

## 🚨 Common Issues & Solutions

### "Failed to connect to server"
- Ensure backend is running: `cd backend && npm run dev`
- Check if port 3001 is available
- Verify `VITE_API_URL` in frontend `.env`

### "Database connection refused"
- Ensure MySQL is running
- Check `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD` in `backend/.env`
- Verify database `neuromate web` exists
- Run migrations if needed

### "Authentication failed"
- Check JWT_SECRET is set in `backend/.env`
- Ensure auth token is stored in localStorage
- Clear browser storage and try again

### "Port already in use"
```bash
# Find and kill process on port 3001 (backend)
netstat -ano | findstr :3001
taskkill /PID <PID> /F

# Find and kill process on port 8080 (frontend)
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

---

## 📚 Resources & References

- **React Documentation:** https://react.dev
- **Vite Documentation:** https://vitejs.dev
- **Express.js Documentation:** https://expressjs.com
- **MySQL Documentation:** https://dev.mysql.com/doc
- **shadcn/ui Components:** https://ui.shadcn.com
- **Tailwind CSS:** https://tailwindcss.com
- **TanStack Query (React Query):** https://tanstack.com/query

---

## 👥 Team

- **Rakesh Telang** - Project Lead / NLP Engineer
- **Abhijit Patil** - Backend Developer
- **Prajakta Patil** - Frontend Developer
- **Navneeth Nair** - AI & Emotion Engineer
- **Jayeed Tamboli** - Documentation & Testing Lead

---

## 📄 License & Notes

This project was created with [Lovable](https://lovable.dev) and is being developed as an open-source mental health companion application.

**Current Status:** Post-migration, ready for feature development

---

**Last Updated:** November 26, 2025
