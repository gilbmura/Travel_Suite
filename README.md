# TravelSuite - Bus Booking Management System

TravelSuite is a comprehensive bus booking management system developed in partnership with Volcano Express, providing online ticket booking services and administrative tools for managing bus operations across Rwanda.

## 🚀 Features

### Customer Frontend
- **Online Booking System**: Easy-to-use interface for booking bus tickets from Nyabugogo and Remera stations to destinations across Rwanda
- **Seat Selection**: Choose preferred seats during booking
- **Province & Sector Selection**: Select destinations by province and sector
- **Booking Confirmation**: Instant confirmation via SMS and email
- **Responsive Design**: Modern, user-friendly interface

### Admin Dashboard
- **Operator Management**: Add and manage bus operators
- **Bus Management**: Add buses with plate numbers, drivers, and capacity
- **Route Management**: Create routes with stopovers, distance, time estimates, and fuel costs
- **Monitoring & Analytics**:
  - View operator activity logs
  - Revenue reports by bus
  - Bus occupancy status tracking
- **Secure Authentication**: Role-based access with bcrypt password hashing

### Operator Dashboard
- **Passenger Check-in**: Mark passengers as checked in
- **Trip Management**: Start trips and mark passenger drop-offs
- **Action Logging**: Automatic logging of all operator actions for audit purposes

## 📋 Prerequisites

- **Python 3.x**
- **MySQL Server** (MariaDB compatible)
- **MySQL Connector** for Python
- **bcrypt** library

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Travel_Suite
   ```

2. **Install Python dependencies**
   ```bash
   pip install mysql-connector-python bcrypt
   ```

3. **Set up MySQL Database**
   - Ensure MySQL Server is running
   - Create a MySQL user (or use existing credentials)
   - Update database credentials in `real_database.py` and `booking_system.py`:
     ```python
     DB_HOST = "localhost"
     DB_USER = "app_user"
     DB_PASSWORD = "AppUser@123"
     DB_NAME = "transport_payments_db"
     ```

4. **Initialize the database**
   ```bash
   python real_database.py
   ```
   This will:
   - Create the database schema
   - Set up all required tables
   - Insert default admin and operator accounts
   - Add sample routes and buses

## 🚦 Usage

### Running the Booking System

1. **Start the backend application**
   ```bash
   python booking_system.py
   ```

2. **Login with default credentials**
   - **Admin**: 
     - Email: `admin@booking.com`
     - Password: `Admin@123`
   - **Operator**: 
     - Email: `operator@booking.com`
     - Password: `Operator@123`

3. **Access the frontend**
   - Open `Frontend/index.html` in a web browser
   - The CSS stylesheet (`Frontend/style.css`) is automatically linked
   - Navigate through the booking interface to make reservations

### Admin Functions

1. **Add Operator**: Create new operator accounts with secure authentication
2. **Add Bus**: Register new buses with plate numbers, drivers, and capacity
3. **Add Route & Stopovers**: Define routes with multiple stopovers and pricing
4. **View Operators**: List all registered operators
5. **View Operator Logs**: Monitor recent operator activities
6. **View Revenue Report**: Analyze revenue by bus
7. **View Bus Occupancy**: Track seat utilization across all buses

### Operator Functions

1. **Check in Passenger**: Mark passengers as checked in using booking ID
2. **Mark Passenger Dropped**: Update booking status when passenger completes journey
3. **Start Trip**: Log trip initiation

## 📊 Database Schema

The system uses the following main tables:

- `admins` - Administrator accounts
- `operators` - Bus operator accounts
- `passengers` - Passenger information
- `buses` - Bus fleet details
- `routes` - Route definitions
- `stopovers` - Route stopover points
- `bus_routes` - Bus-route assignments
- `bookings` - Ticket bookings and status
- `operator_actions` - Audit log of operator activities

## 🔒 Security Features

- **Password Hashing**: All passwords are hashed using bcrypt
- **Role-Based Access**: Separate admin and operator dashboards
- **Audit Logging**: All operator actions are logged with timestamps
- **Secure Authentication**: Email-based login with encrypted passwords

## 📁 Project Structure

```
Travel_Suite/
├── booking_system.py       # Main application (Admin & Operator dashboards)
├── real_database.py        # Database setup and initialization script
├── Frontend/
│   ├── index.html          # Customer-facing booking website
│   └── style.css           # Frontend stylesheet
└── README.md               # This file
```

## 🌍 Supported Locations

- **Departure Stations**: Nyabugogo, Remera
- **Destinations**: All provinces and sectors across Rwanda
- **Operating Hours**: Daily 6:00 AM - 9:00 PM (21:00)

## 🤝 Partnership

TravelSuite operates in partnership with **Volcano Express**, providing quality bus services across Rwanda.

## 📝 Default Credentials

**⚠️ IMPORTANT**: Change default passwords in production environments!

- **Admin Account**:
  - Email: `admin@booking.com`
  - Password: `Admin@123`

- **Operator Account**:
  - Email: `operator@booking.com`
  - Password: `Operator@123`

## 🔧 Configuration

Update the following constants in both `booking_system.py` and `real_database.py` to match your MySQL setup:

```python
DB_HOST = "localhost"
DB_USER = "app_user"
DB_PASSWORD = "AppUser@123"
DB_NAME = "transport_payments_db"
```

## 📞 Contact

- **Email**: info@travelsuite.rw
- **Phone**: +250 788 XXX XXX
- **Locations**: 
  - Nyabugogo Bus Station, Kigali
  - Remera Bus Terminal, Kigali

## 📄 License

[Specify your license here]

## 🚧 Future Enhancements

- Payment gateway integration
- Real-time seat availability
- SMS/Email notification system
- Mobile application
- Advanced reporting and analytics
- Multi-language support

---

**Note**: This is a command-line based administrative system. The frontend (`Frontend/index.html`) is a static HTML interface that would need backend API integration for full functionality.

