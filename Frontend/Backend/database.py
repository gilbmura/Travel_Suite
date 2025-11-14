#!/usr/bin/python3
"""
Transport System Database Auto-Setup Script
This script:
1. Prompts for MySQL root credentials
2. Prompts for new app user credentials
3. Creates a new MySQL user with full privileges
4. Creates a database
5. Creates tables and inserts sample data
"""

import mysql.connector
import getpass

# --- Prompt for credentials ---
print("=== Transport Database Setup ===")

root_user = input("Enter MySQL root username (default: root): ") or "root"
root_password = getpass.getpass("Enter MySQL root password: ")

new_user = input("Enter name for new MySQL app user (e.g. app_user): ")
new_pass = getpass.getpass(f"Enter password for {new_user}: ")
default_db = "transport_payments_db"
db_name = input(
    "Enter database name (e.g. transport_payments_db): "
) or default_db

# --- Connect to MySQL as root ---
try:
    root_conn = mysql.connector.connect(
        host="localhost",
        user=root_user,
        password=root_password
    )
    root_cursor = root_conn.cursor()
    print("Connected to MySQL as root.")
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    exit(1)

# --- Create Database ---
try:
    root_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    print(f"Database '{db_name}' created or already exists.")
except mysql.connector.Error as err:
    print(f" Failed creating database: {err}")
    exit(1)

# --- Create new user and grant privileges ---
try:
    root_cursor.execute(
        f"CREATE USER IF NOT EXISTS '{new_user}'@'localhost' "
        f"IDENTIFIED BY '{new_pass}'"
    )
    grant_query = (
        f"GRANT ALL PRIVILEGES ON {db_name}.* "
        f"TO '{new_user}'@'localhost'"
    )
    root_cursor.execute(grant_query)
    root_cursor.execute("FLUSH PRIVILEGES")
    print(f"MySQL user '{new_user}' created with full access to '{db_name}'.")
except mysql.connector.Error as err:
    print(f"Error creating user or granting privileges: {err}")

root_conn.commit()
root_cursor.close()
root_conn.close()

# --- Reconnect as new app user ---
try:
    conn = mysql.connector.connect(
        host="localhost",
        user=new_user,
        password=new_pass,
        database=db_name
    )
    cursor = conn.cursor()
    print(f"Connected to '{db_name}' as '{new_user}'.")
except mysql.connector.Error as err:
    print(f"Error reconnecting as {new_user}: {err}")
    exit(1)

# --- Define tables ---
TABLES = {}

TABLES['auth_user'] = """
CREATE TABLE IF NOT EXISTS auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_operator BOOLEAN DEFAULT FALSE,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    national_id VARCHAR(25) UNIQUE,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(254),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

TABLES['AdminProfile'] = """
CREATE TABLE IF NOT EXISTS AdminProfile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);
"""

TABLES['OperatorProfile'] = """
CREATE TABLE IF NOT EXISTS OperatorProfile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);
"""

TABLES['Customer'] = """
CREATE TABLE IF NOT EXISTS Customer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    national_id VARCHAR(25) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""

TABLES['Routes'] = """
CREATE TABLE IF NOT EXISTS Routes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME,
    stops TEXT,
    fare DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""

TABLES['Vehicle'] = """
CREATE TABLE IF NOT EXISTS Vehicle (
    id INT AUTO_INCREMENT PRIMARY KEY,
    license_plate VARCHAR(20) NOT NULL UNIQUE,
    route_id INT REFERENCES Routes(id) ON DELETE SET NULL,
    capacity INT NOT NULL CHECK (capacity > 0),
    available_seats INT NOT NULL CHECK (available_seats >= 0),
    status VARCHAR(12) DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""

TABLES['Booking'] = """
CREATE TABLE IF NOT EXISTS Booking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES Customer(id) ON DELETE CASCADE,
    route_id INT REFERENCES Routes(id) ON DELETE SET NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(10) DEFAULT 'Pending',
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""

TABLES['Ticket'] = """
CREATE TABLE IF NOT EXISTS Ticket (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL UNIQUE REFERENCES Booking(id) ON DELETE CASCADE,
    qr_code TEXT NOT NULL UNIQUE,
    is_used BOOLEAN DEFAULT FALSE,
    validated_at TIMESTAMP
);
"""

TABLES['Payments'] = """
CREATE TABLE IF NOT EXISTS Payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL REFERENCES Booking(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(12) NOT NULL,
    status VARCHAR(10) DEFAULT 'Pending',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

TABLES['Transaction'] = """
CREATE TABLE IF NOT EXISTS Transaction (
    id INT AUTO_INCREMENT PRIMARY KEY,
    payment_id INT NOT NULL REFERENCES Payments(id) ON DELETE CASCADE,
    booking_id INT NOT NULL REFERENCES Booking(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    payment_status VARCHAR(10) DEFAULT 'Success',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# --- Create tables ---
for name, ddl in TABLES.items():
    try:
        cursor.execute(ddl)
        print(f"Table '{name}' created successfully.")
    except mysql.connector.Error as err:
        print(f"Error creating table {name}: {err}")

conn.commit()
cursor.close()
conn.close()
print(" All setup complete! Database and tables are ready.")
