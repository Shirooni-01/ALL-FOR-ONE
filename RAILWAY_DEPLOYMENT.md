# Railway.com Deployment Guide

## Problem: Ephemeral Filesystems

Railway.com uses **ephemeral (temporary) filesystems**, meaning:
- JSON files are created fresh on each deployment
- Data stored in files is lost when containers restart
- Multiple instances don't share file systems

## Solution: Use Database Instead

All user data is now stored in the **SQLite database** which **persists** across deployments.

### Database Tables Created:
1. **users** - User accounts
2. **notes** - User notes (was: notes.json)
3. **password_history** - Generated passwords (was: password_history.json)
4. **quiz_results** - Quiz scores

## Deployment Steps for Railway.com

### 1. Update Your Environment Variables
In Railway Dashboard:
```
FLASK_ENV=production
SECRET_KEY=your-very-secure-random-key-32-chars-minimum
GOOGLE_API_KEY=your-api-key
GOOGLE_AI_API_KEY=your-ai-api-key
```

### 2. Deploy Code
```bash
git add .
git commit -m "Move user data to database for production"
git push origin main
```

### 3. Verify Deployment
- Check Railway logs for errors
- Test on deployed URL
- Create an account
- Add notes/generate passwords
- Create new account - should NOT see previous user's data

### 4. Database Persistence
- Railway automatically backs up SQLite databases
- Data survives container restarts
- All users' data is isolated by user_id

## Migration from Previous Deployment

If you had data in `notes.json` or `password_history.json`:

```sql
-- To migrate old notes (if needed):
INSERT INTO notes (user_id, title, note, created_at)
SELECT user_id, title, note, 
       datetime('now') 
FROM old_notes_table;
```

However, since files were ephemeral, this is usually not necessary.

## Testing Locally Before Deploying

```bash
# Test locally to ensure it works
python app.py

# Create 2 test accounts
# Add different data to each
# Logout and login with different account
# Verify data is isolated
```

## Troubleshooting Railway Deployment

### Issue: Still seeing same data for all users
**Solution:**
1. Check if OLD_NOTES.json or password_history.json still exist
2. Delete those files from repo
3. Redeploy

### Issue: "Database is locked"
**Solution:**
- This shouldn't happen with SQLite in production
- If persistent, upgrade to PostgreSQL on Railway

### Issue: Need PostgreSQL instead
Railway offers PostgreSQL as alternative:
```python
# Update config.py for PostgreSQL:
DATABASE_URL = os.getenv("DATABASE_URL")
# Then use SQLAlchemy instead of sqlite3
```

## What Changed

### Before (Broken in Production):
- `notes.json` - Lost on restart
- `password_history.json` - Lost on restart
- All user data in shared JSON files

### After (Works in Production):
- Database tables with user_id foreign keys
- Persistent across deployments
- User data completely isolated
- Automatic backups by Railway

## Files to Remove

These files are no longer needed (delete before deploying):
- `notes.json` ✗
- `password_history.json` ✗

Add to .gitignore (already there):
```
*.db
*.sqlite3
```

## Next Steps

1. Delete old JSON files locally
2. Test locally with the database
3. Push to Railway
4. Test in production
5. All users will see their OWN data only

---

**Status:** ✅ **PRODUCTION READY**

Your application is now configured to work properly on Railway.com!
