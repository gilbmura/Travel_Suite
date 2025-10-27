"""
Online Bus Booking Database Setup Script
----------------------------------------
This script connects to MySQL, creates the database schema,
sets up authorization for admin and operators, and inserts sample data.
"""

import mysql.connector
# from mysql.connector import errorcode
import bcrypt

# --- CONFIGURATION ---
DB_HOST = "localhost"
DB_USER = "app_user"
DB_PASSWORD = "AppUser@123"
DB_NAME = "transport_payments_db"

# --- CONNECT TO MYSQL ---
try:
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    print("Connected to MySQL server successfully.")
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    exit(1)

# --- CREATE DATABASE ---
try:
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    print(f"Database '{DB_NAME}' created or already exists.")
except mysql.connector.Error as err:
    print(f"Failed creating database: {err}")
    exit(1)

cursor.execute(f"USE {DB_NAME}")

# --- TABLE CREATION QUERIES ---
TABLES = {}

TABLES['admins'] = """
CREATE TABLE IF NOT EXISTS admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

TABLES['operators'] = """
CREATE TABLE IF NOT EXISTS operators (
    operator_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active',
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

TABLES['passengers'] = """
CREATE TABLE IF NOT EXISTS passengers (
    passenger_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

TABLES['buses'] = """
CREATE TABLE IF NOT EXISTS buses (
    bus_id INT AUTO_INCREMENT PRIMARY KEY,
    plate_number VARCHAR(20) UNIQUE NOT NULL,
    driver_name VARCHAR(100),
    capacity INT NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active'
);
"""

TABLES['routes'] = """
CREATE TABLE IF NOT EXISTS routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    route_name VARCHAR(100) NOT NULL,
    distance_km DECIMAL(6,2),
    estimated_time_minutes INT,
    fuel_cost DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

TABLES['stopovers'] = """
CREATE TABLE IF NOT EXISTS stopovers (
    stopover_id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    stop_name VARCHAR(100) NOT NULL,
    stop_order INT NOT NULL,
    time_difference_minutes INT,
    FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE
);
"""

TABLES['bus_routes'] = """
CREATE TABLE IF NOT EXISTS bus_routes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bus_id INT NOT NULL,
    route_id INT NOT NULL,
    FOREIGN KEY (bus_id) REFERENCES buses(bus_id) ON DELETE CASCADE,
    FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE
);
"""

TABLES['bookings'] = """
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    passenger_id INT NOT NULL,
    bus_id INT NOT NULL,
    seat_number INT NOT NULL,
    start_stop INT NOT NULL,
    end_stop INT NOT NULL,
    price DECIMAL(10,2),
    status ENUM('booked', 'checked_in', 'cancelled', 'completed') DEFAULT 'booked',
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
    FOREIGN KEY (bus_id) REFERENCES buses(bus_id)
);
"""

TABLES['operator_actions'] = """
CREATE TABLE IF NOT EXISTS operator_actions (
    action_id INT AUTO_INCREMENT PRIMARY KEY,
    operator_id INT NOT NULL,
    action_type VARCHAR(100),
    description TEXT,
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operator_id) REFERENCES operators(operator_id)
);
"""

# --- CREATE TABLES ---
for table_name, ddl in TABLES.items():
    try:
        cursor.execute(ddl)
        print(f"Table '{table_name}' created successfully.")
    except mysql.connector.Error as err:
        print(f"Error creating table {table_name}: {err}")

# --- INSERT SAMPLE DATA ---


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


try:
    # Insert Admin
    cursor.execute("SELECT COUNT(*) FROM admins")
    if cursor.fetchone()[0] == 0:
        admin_pass = hash_password("Admin@123")
        cursor.execute("""
            INSERT INTO admins (full_name, email, password_hash)
            VALUES (%s, %s, %s)
        """, ("System Admin", "admin@booking.com", admin_pass))
        print("Default admin created: admin@booking.com / Admin@123")

    # Insert Operator
    cursor.execute("SELECT COUNT(*) FROM operators")
    if cursor.fetchone()[0] == 0:
        op_pass = hash_password("Operator@123")
        cursor.execute("""
            INSERT INTO operators (full_name, email, password_hash)
            VALUES (%s, %s, %s)
        """, ("John Doe", "operator@booking.com", op_pass))
        print("Default operator created: operator@booking.com / Operator@123")

    # Sample Route and Bus
    cursor.execute("INSERT IGNORE INTO routes (route_name, distance_km, estimated_time_minutes, fuel_cost) VALUES ('Kigali - Kayonza', 75.5, 90, 15000)")
    cursor.execute("INSERT IGNORE INTO buses (plate_number, driver_name, capacity) VALUES ('RAE567X', 'Kamanzi Peter', 30)")
    conn.commit()

    print("Sample data inserted successfully.")

except mysql.connector.Error as err:
    print(f"Error inserting sample data: {err}")

# --- CLOSE CONNECTION ---
cursor.close()
conn.close()
print("Database setup complete.")
