"""
Online Bus Booking Management System
-------------------------------------
Includes:
- Database connection
- Secure login for Admins & Operators
- Admin dashboard for control and monitoring
- Operator dashboard for bus check-ins and drops
"""

import mysql.connector
import bcrypt
import getpass

DB_HOST = "localhost"
DB_USER = "app_user"
DB_PASSWORD = "AppUser@123"
DB_NAME = "transport_payments_db"

# --- Connect to Database ---
conn = mysql.connector.connect(
    host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
)
cursor = conn.cursor(dictionary=True)

# --- Authentication Function ---


def login_user():
    print("=== Login ===")
    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")

    cursor.execute("""
        SELECT 'admin' AS role, admin_id AS id, full_name, password_hash
        FROM admins WHERE email = %s
        UNION
        SELECT 'operator' AS role, operator_id AS id, full_name, password_hash
        FROM operators WHERE email = %s
    """, (email, email))
    user = cursor.fetchone()

    if not user:
        print("Invalid email or password.")
        return None

    if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        print(f"Logged in as {user['role'].capitalize()} ({user['full_name']})")
        return user
    else:
        print("Incorrect password.")
        return None


# --- ADMIN FUNCTIONS ---

def view_operator_logs():
    cursor.execute("""
        SELECT a.action_id, o.full_name AS operator, a.action_type, a.description, a.action_time
        FROM operator_actions a
        JOIN operators o ON a.operator_id = o.operator_id
        ORDER BY a.action_time DESC
        LIMIT 20
    """)
    logs = cursor.fetchall()
    print("\n--- Recent Operator Actions ---")
    for log in logs:
        print(f"[{log['action_time']}] {log['operator']} - {log['action_type']} → {log['description']}")


def view_revenue_by_bus():
    cursor.execute("""
        SELECT b.plate_number, SUM(price) AS total_revenue, COUNT(*) AS trips
        FROM bookings k
        JOIN buses b ON k.bus_id = b.bus_id
        WHERE k.status IN ('checked_in', 'completed')
        GROUP BY b.plate_number
        ORDER BY total_revenue DESC
    """)
    results = cursor.fetchall()
    print("\n--- Revenue by Bus ---")
    for r in results:
        print(f"Bus {r['plate_number']} | Total Revenue: {r['total_revenue']} Frw | Trips: {r['trips']}")


def view_bus_occupancy():
    cursor.execute("""
        SELECT b.plate_number,
               COUNT(CASE WHEN k.status='booked' THEN 1 END) AS booked,
               COUNT(CASE WHEN k.status='checked_in' THEN 1 END) AS onboard,
               COUNT(CASE WHEN k.status='completed' THEN 1 END) AS completed,
               b.capacity
        FROM buses b
        LEFT JOIN bookings k ON b.bus_id = k.bus_id
        GROUP BY b.plate_number, b.capacity
    """)
    rows = cursor.fetchall()
    print("\n--- Bus Occupancy Status ---")
    for row in rows:
        total = row['booked'] + row['onboard']
        print(f"Bus {row['plate_number']}: {total}/{row['capacity']} seats used "
              f"({row['booked']} booked, {row['onboard']} onboard, {row['completed']} completed)")


def admin_menu(admin):
    while True:
        print("\n--- ADMIN DASHBOARD ---")
        print("1. Add Operator")
        print("2. Add Bus")
        print("3. Add Route & Stopovers")
        print("4. View Operators")
        print("5. View Operator Logs")
        print("6. View Revenue Report by Bus")
        print("7. View Bus Occupancy")
        print("8. Exit")
        choice = input("Select option: ")

        if choice == "1":
            name = input("Full name: ")
            email = input("Email: ")
            password = getpass.getpass("Password: ")
            hash_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            cursor.execute("""
                INSERT INTO operators (full_name, email, password_hash)
                VALUES (%s, %s, %s)
            """, (name, email, hash_pw))
            conn.commit()
            print("Operator added successfully.")

        elif choice == "2":
            plate = input("Bus Plate Number: ")
            driver = input("Driver Name: ")
            capacity = int(input("Capacity: "))
            cursor.execute("""
                INSERT INTO buses (plate_number, driver_name, capacity)
                VALUES (%s, %s, %s)
            """, (plate, driver, capacity))
            conn.commit()
            print("Bus added successfully.")

        elif choice == "3":
            route = input("Route Name: ")
            dist = float(input("Distance (km): "))
            time = int(input("Estimated Time (minutes): "))
            fuel = float(input("Fuel Cost (Frw): "))
            cursor.execute("""
                INSERT INTO routes (route_name, distance_km, estimated_time_minutes, fuel_cost)
                VALUES (%s, %s, %s, %s)
            """, (route, dist, time, fuel))
            route_id = cursor.lastrowid
            print("Now add stopovers:")
            while True:
                stop = input("Stopover name (or 'done'): ")
                if stop.lower() == "done":
                    break
                order = int(input("Stop order: "))
                diff = int(input("Time difference (minutes): "))
                cursor.execute("""
                    INSERT INTO stopovers (route_id, stop_name, stop_order, time_difference_minutes)
                    VALUES (%s, %s, %s, %s)
                """, (route_id, stop, order, diff))
            conn.commit()
            print("Route and stopovers added successfully.")

        elif choice == "4":
            cursor.execute("SELECT operator_id, full_name, email, status FROM operators")
            for op in cursor.fetchall():
                print(op)

        elif choice == "5":
            view_operator_logs()

        elif choice == "6":
            view_revenue_by_bus()

        elif choice == "7":
            view_bus_occupancy()

        elif choice == "8":
            break

        else:
            print("Invalid option.")


# --- OPERATOR FUNCTIONS ---

def operator_menu(operator):
    while True:
        print("\n--- OPERATOR DASHBOARD ---")
        print("1. Check in Passenger")
        print("2. Mark Passenger Dropped")
        print("3. Start Trip")
        print("4. Exit")
        choice = input("Select option: ")

        if choice == "1":
            booking_id = input("Enter booking ID: ")
            cursor.execute("UPDATE bookings SET status='checked_in' WHERE booking_id=%s", (booking_id,))
            conn.commit()
            cursor.execute("INSERT INTO operator_actions (operator_id, action_type, description) VALUES (%s, %s, %s)",
                           (operator['id'], 'check_in', f"Checked in booking {booking_id}"))
            conn.commit()
            print("Passenger checked in.")

        elif choice == "2":
            booking_id = input("Enter booking ID: ")
            cursor.execute("UPDATE bookings SET status='completed' WHERE booking_id=%s", (booking_id,))
            conn.commit()
            cursor.execute("INSERT INTO operator_actions (operator_id, action_type, description) VALUES (%s, %s, %s)",
                           (operator['id'], 'drop_off', f"Passenger dropped from booking {booking_id}"))
            conn.commit()
            print("Passenger dropped.")

        elif choice == "3":
            bus_id = input("Enter bus ID: ")
            cursor.execute("INSERT INTO operator_actions (operator_id, action_type, description) VALUES (%s, %s, %s)",
                           (operator['id'], 'start_trip', f"Started trip for bus {bus_id}"))
            conn.commit()
            print("Trip started.")

        elif choice == "4":
            break

        else:
            print("Invalid option.")


# --- MAIN PROGRAM ---
if __name__ == "__main__":
    user = login_user()
    if user:
        if user['role'] == 'admin':
            admin_menu(user)
        elif user['role'] == 'operator':
            operator_menu(user)

    cursor.close()
    conn.close()
    print("Session ended.")
