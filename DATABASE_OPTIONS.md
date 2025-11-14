# TravelSuite - Database Configuration & Options

## Current Status

**Active Database:** SQLite (`db.sqlite3`)
**Status:** ✅ Fully Functional
**Data:** Pre-populated with seed data

---

## Available Options

### Option 1: Continue with SQLite (RECOMMENDED - Currently Working)
- ✅ **Status:** Fully functional and tested
- ✅ **All APIs working:** 100% operational
- ✅ **Frontend connected:** All endpoints accessible
- ✅ **Data populated:** Routes, vehicles, customers ready
- ✅ **No external dependencies:** Works out of the box
- ✅ **Development friendly:** Perfect for testing and development

**Advantages:**
- Zero configuration needed
- No MySQL setup required
- File-based database (portable)
- Perfect for development/testing

**Disadvantages:**
- Not ideal for production with many concurrent users
- Slower than MySQL for large datasets

**Keep Using:** Continue with current setup

---

### Option 2: Switch to MySQL (Requires MySQL Server)

**Files Involved:**
- `dta.py` - MySQL database creation script
- `config/settings.py` - Django database configuration
- `requirements.txt` - Already includes mysql-connector-python

**What Needs to Be Done:**
1. Install and start MySQL server locally
2. Run `dta.py` to create database and tables
3. Update `config/settings.py` with MySQL connection settings
4. Run Django migrations
5. Seed the database

**Prerequisites:**
- MySQL Server must be installed and running on `localhost:3306`
- MySQL root user with a known password
- OR modify `dta.py` with appropriate credentials

**Current Issue:** MySQL server is not detected on this system

---

### Option 3: Docker-based MySQL

If you want to use MySQL without installing it:

```bash
# Run MySQL in Docker
docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root mysql:8.0

# Then run dta.py
python dta.py
```

---

## Recommendation

**For Development/Testing:** Use **Option 1 (SQLite)** ✅ - Currently fully functional

**For Production:** Use **Option 2 (MySQL)** or **Option 3 (Docker)**

---

## If You Want to Switch to MySQL

### Step 1: Ensure MySQL is Running
```bash
# Windows:
net start MySQL80

# Or check if already running:
mysql -u root -p
```

### Step 2: Run Database Setup
```bash
python dta.py
# Follow prompts for credentials
```

### Step 3: Update Django Settings
Edit `config/settings.py` and change:

```python
# OLD (SQLite):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# NEW (MySQL):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'transport_payments_db',
        'USER': 'app_user',
        'PASSWORD': 'your_password_here',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Step 4: Apply Migrations
```bash
python manage.py migrate
```

### Step 5: Seed Data
```bash
python manage.py seed_data
```

### Step 6: Restart Server
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## Current Database Schema

Both SQLite and MySQL use the same Django models:

### Tables
- `auth_user` - User accounts (Admin, Operator)
- `core_customer` - Customer information
- `core_route` - Bus routes
- `core_vehicle` - Vehicles/Buses
- `core_seat` - Seat inventory
- `core_booking` - Ticket reservations
- `core_ticket` - Ticket validation
- `core_payment` - Payment records
- `core_transaction` - Transaction history
- `core_event` - Events
- `core_adminprofile` - Admin profiles
- `core_operatorprofile` - Operator profiles

---

## Data Already in Database

### Routes (3)
1. Nyabugogo → Muhanga - 8:00 AM - RWF 5,000
2. Remera → Gitarama - 10:00 AM - RWF 8,000
3. Nyabugogo → Ruhengeri - 6:00 AM - RWF 12,000

### Vehicles (3)
1. RW001BUS - 50 seats
2. RW002BUS - 45 seats
3. RW003BUS - 60 seats

### Customers (3)
1. John Doe - +250788333333
2. Jane Smith - +250788444444
3. Bob Johnson - +250788555555

### Users
- Admin: admin / Admin@123
- Operator: operator / Operator@123

---

## API Testing with Current Setup

All endpoints are working with SQLite:

```bash
# Get token
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}'

# Access any endpoint
curl -X GET http://127.0.0.1:8000/api/routes/ \
  -H "Authorization: Bearer {token}"
```

---

## Migration Path (If You Switch Later)

To migrate from SQLite to MySQL without losing data:

```bash
# 1. Backup SQLite data
python manage.py dumpdata > backup.json

# 2. Configure MySQL
# Edit config/settings.py

# 3. Create MySQL database
python dta.py

# 4. Apply migrations
python manage.py migrate

# 5. Restore data
python manage.py loaddata backup.json
```

---

## Summary

| Aspect | SQLite | MySQL |
|--------|--------|-------|
| Status | ✅ Working | ⏳ Needs MySQL server |
| Performance | Good | Better for scale |
| Setup | None needed | Run dta.py |
| Configuration | Simple | More config |
| Development | ✅ Perfect | Suitable |
| Production | Limited | ✅ Better |

**Current Recommendation: Keep SQLite - All systems operational**

---

**Last Updated:** November 13, 2025
