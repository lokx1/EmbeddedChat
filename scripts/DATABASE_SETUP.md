# EmbeddedChat Backend Database Setup Guide

## Prerequisites
- PostgreSQL installed and running
- Database `EmbeddedAI` created in PostgreSQL
- Python 3.8+ installed

## Step-by-Step Setup

### 1. Install Dependencies
```bash
install.bat
```

### 2. Configure Database Connection
Edit the `.env` file and update the database URL with your PostgreSQL credentials:

```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/EmbeddedAI
```

Replace `YOUR_PASSWORD` with your PostgreSQL password.

### 3. Test Database Connection
```bash
# Activate virtual environment first
venv\Scripts\activate.bat

# Test connection
python setup_db.py test
```

### 4. Create Database Tables
```bash
python setup_db.py create
```

### 5. Run the Application
```bash
run.bat
```

## Alternative: One-Click Setup
After updating your `.env` file, you can run:
```bash
setup_database.bat
```

This will automatically test the connection and create all tables.

## Database Commands

### Test Connection
```bash
python setup_db.py test
```

### Create Tables
```bash
python setup_db.py create
```

### Drop All Tables (⚠️ Dangerous!)
```bash
python setup_db.py drop
```

## Troubleshooting

### Connection Issues
1. Make sure PostgreSQL is running
2. Verify database `EmbeddedAI` exists
3. Check username/password in `.env`
4. Ensure port 5432 is correct

### Permission Issues
Make sure your PostgreSQL user has permissions to:
- Connect to database
- Create/drop tables
- Insert/update/delete data

### Database Not Found
Create the database in PostgreSQL:
```sql
CREATE DATABASE "EmbeddedAI";
```

## What Tables Will Be Created?

The setup will create these tables:
- `users` - User accounts and authentication
- `conversations` - Chat conversations
- `messages` - Individual messages in conversations
- `documents` - Uploaded documents for RAG

## API Documentation
Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
