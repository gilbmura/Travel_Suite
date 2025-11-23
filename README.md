# Travel Suite

A Rwanda-focused travel booking system with real-time seat availability, operator-assisted cash bookings, and auto-refund cancellations.

## Features

- **Guest Bookings**: Search routes, view schedules, book tickets (MTN/Airtel payment), receive SMS + email with QR ticket
- **Operator Dashboard**: Create cash bookings, mark schedules as departed, view assigned routes
- **Admin Dashboard**: Full CRUD for buses, routes, schedules, and operator assignments
- **Real-time Seat Availability**: Live updates on remaining seats
- **Auto-refund Cancellations**: Automatic refunds for cancellations >1 hour before departure
- **Recurring Schedules**: Support for daily/weekly recurring schedules

## MVP Status

**Important**: This is a **Minimum Viable Product (MVP)** designed for demonstration and development purposes. As such, certain external services use placeholder credentials and will not function until real credentials are configured.

### What Works in MVP Mode

**Fully Functional:**
- Route and schedule management
- Booking creation and management
- Seat availability tracking
- Payment processing (mocked)
- Operator and admin dashboards
- Database operations
- All core booking features

**Not Configured (Expected in MVP):**
- **SMS Notifications (Twilio)**: Uses placeholder credentials - SMS will not be sent, but bookings will still work
- **Email Notifications**: Uses placeholder SMTP settings - emails will not be sent, but bookings will still work
- **Real Payment Processing**: Payments are mocked by default - transactions are simulated

### Why External Services Don't Work

The MVP includes placeholder credentials for external services to demonstrate the integration points. This is **intentional and expected**:

1. **Twilio SMS**: The system attempts to send SMS but will fail with authentication errors if placeholder credentials are used. This is normal for MVP - bookings are still created successfully.

2. **Email (SMTP)**: Email sending will fail with placeholder SMTP credentials. This is normal for MVP - bookings are still created successfully.

3. **Payment Processing**: Payments are mocked by default (`PAYMENTS_MODE=mock`). Real payment processing requires integration with actual MTN/Airtel APIs.

### For Production Use

To enable these services in production:
1. **Twilio**: Sign up at https://www.twilio.com/ and add real credentials to `.env`
2. **Email**: Configure real SMTP settings (Gmail, SendGrid, etc.) in `.env`
3. **Payments**: Replace mock adapters with real MTN/Airtel API integrations

**Note**: Bookings will work perfectly fine without these services - they are optional enhancements for notifications and payment processing.

## Tech Stack

- **Backend**: Python 3.10+, Django 4.x, Django REST Framework
- **Database**: MySQL (using PyMySQL for easy Windows installation)
- **Frontend**: Vanilla JavaScript, Responsive HTML/CSS
- **SMS**: Twilio (placeholder credentials in MVP - requires real credentials for production)
- **Payments**: MTN + Airtel (mocked adapters in MVP, `PAYMENTS_MODE=mock|live`)
- **Email**: SMTP (placeholder settings in MVP - requires real SMTP credentials for production)

## Installation

### Prerequisites

- Python 3.10 or higher
- MySQL 5.7+ or 8.0+
- pip

### Database Setup (MySQL with PyMySQL)

This project uses **PyMySQL** for easy installation across all platforms (no compilation required on Windows, minimal setup on Linux/Mac).

#### Windows Setup

1. **Install MySQL Server** (if not already installed):
   - Download from: https://dev.mysql.com/downloads/mysql/
   - Or use XAMPP/WAMP which includes MySQL
   - Make sure MySQL service is running (check via Services or Task Manager)

2. **Create MySQL database**:
   ```sql
   -- Open MySQL command line or MySQL Workbench
   CREATE DATABASE travel_suite CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
   
   Or using MySQL command line:
   ```bash
   mysql -u root -p
   CREATE DATABASE travel_suite CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   ```

#### Linux Setup

1. **Install MySQL Server**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install mysql-server
   
   # Fedora/RHEL/CentOS
   sudo dnf install mysql-server
   # or
   sudo yum install mysql-server
   
   # Arch Linux
   sudo pacman -S mysql
   ```

2. **Start MySQL service**:
   ```bash
   # Ubuntu/Debian (systemd)
   sudo systemctl start mysql
   sudo systemctl enable mysql
   
   # Set root password (if not set during installation)
   sudo mysql_secure_installation
   ```

3. **Create MySQL database**:
   ```bash
   mysql -u root -p
   ```
   ```sql
   CREATE DATABASE travel_suite CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   ```

#### macOS Setup

1. **Install MySQL Server**:
   ```bash
   # Using Homebrew (recommended)
   brew install mysql
   
   # Or download from: https://dev.mysql.com/downloads/mysql/
   ```

2. **Start MySQL service**:
   ```bash
   # Using Homebrew
   brew services start mysql
   
   # Or manually
   mysql.server start
   ```

3. **Set root password** (if not set):
   ```bash
   mysql_secure_installation
   ```

4. **Create MySQL database**:
   ```bash
   mysql -u root -p
   ```
   ```sql
   CREATE DATABASE travel_suite CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   ```

#### Note MySQL Credentials

For all platforms, note your MySQL credentials:
- Username (usually `root`)
- Password (if set)
- Host (usually `localhost`)
- Port (usually `3306`)

### Setup Steps

1. **Clone the repository** (or extract files):
   ```bash
   git clone <repository-url>
   cd Travel_Suite
   ```

2. **Create a virtual environment**:
   
   **Windows**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   
   **Linux/Mac**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   You should see `(venv)` in your terminal prompt when activated.

3. **Install dependencies**:
   ```bash
   # Windows
   pip install -r requirements.txt
   
   # Linux/Mac (use pip3 if python3 is not default)
   pip install -r requirements.txt
   # or
   pip3 install -r requirements.txt
   ```
   
   **Note**: PyMySQL is included in requirements.txt and will be installed automatically. On Windows, no compilation is needed. On Linux/Mac, PyMySQL installs easily via pip.

4. **Set up environment variables**:
   
   Create a `.env` file in the project root with the following content:
   ```env
   # Django Settings
   SECRET_KEY=your-secret-key-here-change-in-production
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database Configuration
   DATABASE_NAME=travel_suite
   DATABASE_USER=root
   DATABASE_PASSWORD=your_mysql_password
   DATABASE_HOST=localhost
   DATABASE_PORT=3306
   
   # Payment Mode (mock for development, live for production)
   PAYMENTS_MODE=mock
   
   # Twilio SMS (optional - use placeholders for MVP)
   TWILIO_ACCOUNT_SID=your-twilio-account-sid
   TWILIO_AUTH_TOKEN=your-twilio-auth-token
   TWILIO_FROM_NUMBER=+1234567890
   
   # Email Settings (optional - use placeholders for MVP)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   EMAIL_FROM=noreply@travelsuite.rw
   ```
   
   **Important**: Replace `your_mysql_password` with your actual MySQL root password (or leave empty if no password is set).
   
   **Platform-specific notes**:
   - **Windows**: Use any text editor (Notepad, VS Code, etc.)
   - **Linux/Mac**: Use `nano`, `vim`, or any text editor:
     ```bash
     nano .env
     # or
     vim .env
     ```

5. **Run migrations**:
   ```bash
   # Windows
   python manage.py migrate
   
   # Linux/Mac
   python manage.py migrate
   # or if python3 is not default
   python3 manage.py migrate
   ```
   
   This will create all necessary database tables.

6. **Create admin superuser**:
   ```bash
   # Windows
   python manage.py createsuperuser
   
   # Linux/Mac
   python manage.py createsuperuser
   # or
   python3 manage.py createsuperuser
   ```
   
   You will be prompted to enter:
   - Username (e.g., `admin`)
   - Email (optional, e.g., `admin@travelsuite.rw`)
   - Password (enter a strong password, e.g., `admin123` - change this in production!)
   
   **Example**:
   ```
   Username: admin
   Email address: admin@travelsuite.rw
   Password: ********
   Password (again): ********
   Superuser created successfully.
   ```

7. **Seed sample data** (optional but recommended):
   ```bash
   # Windows
   python manage.py seed_sample_data
   
   # Linux/Mac
   python manage.py seed_sample_data
   # or
   python3 manage.py seed_sample_data
   ```
   
   This creates sample districts, routes, buses, schedules, and operators for testing.

8. **Generate future schedule occurrences**:
   ```bash
   # Windows
   python manage.py generate_schedule_occurrences --days 60
   
   # Linux/Mac
   python manage.py generate_schedule_occurrences --days 60
   # or
   python3 manage.py generate_schedule_occurrences --days 60
   ```
   
   This ensures schedule occurrences are available for the next 60 days.

9. **Run the development server**:
   ```bash
   # Windows
   python manage.py runserver
   
   # Linux/Mac
   python manage.py runserver
   # or
   python3 manage.py runserver
   ```
   
   The server will start on `http://127.0.0.1:8000/` by default.

10. **Access the application**:
    - **Frontend (Guest)**: http://localhost:8000/
    - **Admin Dashboard**: http://localhost:8000/admin/
    - **Django Admin (Advanced)**: http://localhost:8000/django-admin/
    - **Operator Login**: http://localhost:8000/operator/login/
    - **API**: http://localhost:8000/api/

### Platform-Specific Notes

#### Windows
- Use `python` command (not `python3`)
- Virtual environment activation: `venv\Scripts\activate`
- No compilation needed for PyMySQL
- MySQL can be installed via installer or XAMPP/WAMP

#### Linux
- May need to use `python3` instead of `python`
- Virtual environment activation: `source venv/bin/activate`
- May need to install Python development headers for some packages:
  ```bash
  # Ubuntu/Debian
  sudo apt install python3-dev python3-pip
  
  # Fedora/RHEL
  sudo dnf install python3-devel python3-pip
  ```
- PyMySQL installs easily via pip

#### macOS
- Use `python3` command (Python 2 is deprecated)
- Virtual environment activation: `source venv/bin/activate`
- Install Homebrew if not already installed: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- PyMySQL installs easily via pip

### Development Platform Note

**Important**: This project was developed and tested on **Windows**. All setup instructions have been verified on Windows 10/11. The Linux and macOS instructions provided above are for cross-platform compatibility and should work, but if you encounter any platform-specific issues, please refer to the Troubleshooting section below.

## Admin Access & Login

### Creating an Admin User

If you haven't created an admin user yet, or need to create additional admin users:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter username, email, and password.

**To create admin from Django shell** (alternative method):
```bash
python manage.py shell
```

Then in the shell:
```python
from accounts.models import User
User.objects.create_superuser(
    username='admin',
    email='admin@travelsuite.rw',
    password='your_secure_password'
)
exit()
```

### Logging In as Admin

1. **Navigate to admin login page**:
   - URL: http://localhost:8000/admin/
   - Or click "Admin Login" from the frontend

2. **Enter credentials**:
   - Username: The username you created (e.g., `admin`)
   - Password: The password you set

3. **Access admin dashboard**:
   - After successful login, you'll be redirected to `/admin/dashboard/`
   - Here you can manage:
     - Districts (locations)
     - Routes
     - Buses
     - Schedule Recurrences
     - Bookings
     - Operators (create, edit, delete operator accounts)
     - Operator Assignments (assign operators to specific routes)

### Admin vs Django Admin

- **Custom Admin Dashboard** (`/admin/`): User-friendly interface for managing the booking system
- **Django Admin** (`/django-admin/`): Advanced Django admin interface for database-level management

Both require the same superuser credentials.

### Operator Management

**Important**: Operators must be created and managed by administrators. Operators cannot self-register.

#### Creating Operators (Admin Only)

1. **Log in to the admin dashboard**: http://localhost:8000/admin/
2. **Navigate to the "Operators" section** in the admin dashboard
3. **Click "Add Operator"** button
4. **Fill in operator details**:
   - Username (must be unique)
   - Password (for operator login)
   - Full Name
   - Phone Number
   - Email (optional)
5. **Click "Save"** to create the operator account

#### Assigning Operators to Routes (Admin Only)

After creating an operator, you must assign them to specific routes:

1. **Navigate to "Operator Assignments"** section in the admin dashboard
2. **Click "Add Assignment"** button
3. **Select**:
   - Operator (from dropdown)
   - Route (from dropdown)
4. **Click "Save"** to assign the operator to that route

**Note**: Operators can only view and manage bookings for routes they are assigned to. They cannot access routes they are not assigned to.

#### Operator Login

Once an operator account is created by an admin, operators can log in:
- URL: http://localhost:8000/operator/login/
- Credentials: Username and password set by the admin
- Default operator (from seed data): `operator1` / `operator123`

**Operator Capabilities**:
- View assigned routes only
- Create cash bookings for assigned routes
- Mark schedules as departed
- View bookings for assigned routes
- Cancel bookings (if cancellable)

## Environment Variables

Create a `.env` file in the project root with these variables:

**Required Variables**:
- `DATABASE_NAME`: MySQL database name (default: `travel_suite`)
- `DATABASE_USER`: MySQL username (default: `root`)
- `DATABASE_PASSWORD`: MySQL password (leave empty if no password)
- `DATABASE_HOST`: MySQL host (default: `localhost`)
- `DATABASE_PORT`: MySQL port (default: `3306`)
- `SECRET_KEY`: Django secret key (generate a new one for production)

**Optional Variables**:
- `PAYMENTS_MODE`: Set to `mock` (default) or `live` for production
- `TWILIO_*`: Twilio SMS credentials (placeholders work for MVP)
- `EMAIL_*`: SMTP settings for email notifications (placeholders work for MVP)
- `DEBUG`: Set to `True` for development, `False` for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Running Tests

```bash
python manage.py test
```

Or run specific test modules:
```bash
python manage.py test bookings.tests
python manage.py test payments.tests
```

## Payment Mode

The system supports two payment modes:

- **`mock`** (default): Simulates payment processing with delays and testable transaction IDs. Use this for development and testing. **This is the default for MVP.**
- **`live`**: Connects to real MTN/Airtel payment APIs. Replace mock adapter methods with actual API calls. **Requires real payment provider integrations.**

To toggle payment mode, set `PAYMENTS_MODE=mock` or `PAYMENTS_MODE=live` in your `.env` file.

**MVP Note**: In MVP mode, payments are mocked by default. All bookings will be processed successfully, but no actual money transactions occur. This allows full testing of the booking system without requiring payment provider accounts.

## API Documentation

See `postman_collection.json` for API endpoint documentation and sample requests/responses.

Key endpoints:
- `GET /api/routes/?from=<location>` - Search routes
- `GET /api/schedules/?route_id=...&date=...` - Get schedule occurrences
- `POST /api/bookings/` - Create guest booking
- `POST /api/bookings/<id>/cancel/` - Cancel booking
- `GET /api/bookings/<id>/status/` - Get booking status
- `POST /api/operator/bookings/` - Create cash booking (operator)
- `POST /api/operator/schedules/<id>/mark_departed/` - Mark schedule as departed

## Performance & Reliability

### Backend Optimizations

- **Query Optimization**: Uses `select_related` and `prefetch_related` for efficient schedule → bus → route queries
- **Database Transactions**: Uses `select_for_update` when creating bookings to prevent overbooking
- **Caching**: Suggested caching for route list and schedule list (per-route cache TTL 1-5 minutes)
- **Pagination**: All list endpoints support pagination

### Frontend Optimizations

- **Real-time Updates**: Frontend polls remaining seats every 30 seconds on schedule pages
- **Optimistic UI**: Updates UI immediately after booking, then syncs with server
- **Async Operations**: All API calls use `fetch` with `async/await`

### Background Tasks

For production, heavy work (email + SMS sending) should be moved to background workers (e.g., Celery). The MVP includes a `send_notification_async()` wrapper that can be connected to a task queue.

### Schedule Occurrence Generation

Schedule occurrences are automatically generated when creating a new schedule recurrence (60 days ahead). To extend future occurrences or regenerate them, run:

```bash
python manage.py generate_schedule_occurrences --days 60
```

**Recommended**: Set up a daily cron job to run this command to ensure future schedule occurrences are always available:

```bash
# Example cron job (runs daily at 2 AM)
0 2 * * * cd /path/to/travel_suite && /path/to/venv/bin/python manage.py generate_schedule_occurrences --days 60
```

## Project Structure

```
travel_suite/
├── accounts/          # User accounts app
├── routes/            # Routes and locations app
├── buses/             # Bus management app
├── bookings/          # Booking management app
├── payments/          # Payment adapters (MTN, Airtel)
├── notifications/     # SMS and email notifications
├── operators/         # Operator management app
├── api/               # API routing and views
├── static/            # Static files (CSS, JS, images)
├── templates/         # HTML templates
├── fixtures/          # Test fixtures
└── manage.py
```

## Security Considerations

See `SECURITY.md` for production security considerations including:
- Environment variable management
- HTTPS requirements
- Rate limiting
- Idempotency keys
- Webhook validation

## Design Guide

See `design-guide.md` for the African-inspired design system, color palette, typography, and CSS utilities.

## Troubleshooting

### Database Connection Issues

**Error**: `django.db.utils.OperationalError: (2003, "Can't connect to MySQL server")`

**Solutions**:
1. **Check MySQL is running**:
   ```bash
   # Windows (check Services)
   services.msc  # Look for MySQL service
   
   # Or check via command line
   mysql -u root -p
   ```

2. **Verify database exists**:
   ```sql
   SHOW DATABASES;
   ```
   Make sure `travel_suite` is listed.

3. **Check credentials in `.env`**:
   - Verify `DATABASE_USER` and `DATABASE_PASSWORD` are correct
   - If MySQL has no password, leave `DATABASE_PASSWORD` empty in `.env`

4. **Test connection manually**:
   ```bash
   mysql -u root -p travel_suite
   ```

**Error**: `ModuleNotFoundError: No module named 'pymysql'`

**Solution**:
```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall requirements
pip install -r requirements.txt
```

**Error**: `django.db.utils.ProgrammingError: (1146, "Table 'travel_suite.xxx' doesn't exist")`

**Solution**:
```bash
# Run migrations
python manage.py migrate
```

### Migration Issues

**Error**: `django.db.migrations.exceptions.InconsistentMigrationHistory`

**Solution**:
```bash
# Reset migrations (WARNING: This deletes data!)
python manage.py migrate --fake-initial

# Or if that doesn't work, reset completely:
python manage.py migrate accounts zero
python manage.py migrate
```

### Admin Login Issues

**Error**: "Invalid username or password"

**Solutions**:
1. **Verify user exists**:
   ```bash
   python manage.py shell
   ```
   ```python
   from accounts.models import User
   User.objects.filter(is_superuser=True)
   # Should show your admin user
   ```

2. **Reset admin password**:
   ```bash
   python manage.py changepassword admin
   ```

3. **Create new admin**:
   ```bash
   python manage.py createsuperuser
   ```

**Error**: "Permission denied" on admin dashboard

**Solution**:
- Make sure the user has `is_staff=True` and `is_superuser=True`:
  ```bash
  python manage.py shell
  ```
  ```python
  from accounts.models import User
  user = User.objects.get(username='admin')
  user.is_staff = True
  user.is_superuser = True
  user.save()
  ```

### Static Files Not Loading

**Error**: CSS/JS files return 404

**Solution**:
```bash
# Collect static files
python manage.py collectstatic --noinput

# Or in development, make sure DEBUG=True in settings
```

### Port Already in Use

**Error**: `Error: That port is already in use`

**Solution**:
```bash
# Use a different port
python manage.py runserver 8001

# Or kill the process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill
```

### PyMySQL Import Errors

**Error**: `ImportError: No module named 'MySQLdb'`

**Solution**:
- Make sure `travel_suite/__init__.py` contains:
  ```python
  import pymysql
  pymysql.install_as_MySQLdb()
  ```
- Verify PyMySQL is installed:
  ```bash
  pip list | grep -i pymysql
  ```

### Schedule Occurrences Not Showing

**Problem**: No schedules available for future dates

**Solution**:
```bash
# Generate schedule occurrences
python manage.py generate_schedule_occurrences --days 60
```

### Payment/SMS/Email Errors

**This is Expected in MVP Mode!**

The following errors are **normal and expected** in MVP mode:

1. **Twilio Authentication Errors**:
   - **Error**: `Authentication Error - invalid username` or `Unable to create record`
   - **Cause**: Placeholder Twilio credentials in `.env` file
   - **Impact**: SMS will not be sent, but **bookings will still work perfectly**
   - **Solution for MVP**: Leave Twilio credentials empty in `.env`:
     ```env
     TWILIO_SID=
     TWILIO_TOKEN=
     TWILIO_FROM=
     ```
   - **Solution for Production**: Add real Twilio credentials from https://www.twilio.com/

2. **Email Sending Failures**:
   - **Error**: SMTP authentication errors or connection failures
   - **Cause**: Placeholder SMTP credentials in `.env` file
   - **Impact**: Emails will not be sent, but **bookings will still work perfectly**
   - **Solution for MVP**: Leave email settings empty or use placeholders
   - **Solution for Production**: Configure real SMTP settings (Gmail, SendGrid, etc.)

3. **Payment Processing**:
   - **Status**: Payments are mocked by default (`PAYMENTS_MODE=mock`)
   - **Impact**: All bookings process successfully with simulated payments
   - **Solution for Production**: Replace mock adapters with real MTN/Airtel API integrations

**Important**: These errors do not prevent bookings from being created. The system is designed to gracefully handle missing external service credentials. Bookings will be created successfully, and you'll see warnings in the logs about SMS/email failures, which is expected behavior for MVP.

**For production**:
- Replace mock adapters in `payments/mt_n_adapter.py` and `payments/airtel_adapter.py`
- Add real Twilio credentials to `.env` (sign up at https://www.twilio.com/)
- Configure real SMTP settings in `.env` (Gmail, SendGrid, AWS SES, etc.)

### Common Windows-Specific Issues

**Issue**: Virtual environment not activating

**Solution**:
```powershell
# PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.\venv\Scripts\Activate.ps1
```

**Issue**: `mysqlclient` installation fails

**Solution**: This project uses PyMySQL instead of mysqlclient, so this shouldn't occur. If you see this error, make sure you're using the correct `requirements.txt`.

### Getting Help

1. **Check Django logs**: Look at the terminal output when running `python manage.py runserver`
2. **Check database**: Verify tables exist with `SHOW TABLES;` in MySQL
3. **Verify environment**: Make sure `.env` file exists and has correct values
4. **Check Python version**: `python --version` should show 3.10 or higher
5. **Verify virtual environment**: Make sure it's activated (you should see `(venv)` in your terminal)

## License

This is an MVP for demonstration purposes.

