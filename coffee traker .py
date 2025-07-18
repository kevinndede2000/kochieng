import sqlite3
import africastalking

# Initialize Africa's Talking
username = "your_username"
api_key = "your_api_key"
africastalking.initialize(username, api_key)
sms = africastalking.SMS

# Initialize DB
conn = sqlite3.connect("coffee.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_name TEXT,
    phone TEXT,
    weight REAL,
    total_weight REAL
)
""")
conn.commit()

def record_delivery(name, phone, new_weight):
    # Check previous total
    cursor.execute("SELECT SUM(weight) FROM deliveries WHERE phone = ?", (phone,))
    result = cursor.fetchone()
    previous_total = result[0] if result[0] else 0

    total = previous_total + new_weight

    # Save new record
    cursor.execute("INSERT INTO deliveries (farmer_name, phone, weight, total_weight) VALUES (?, ?, ?, ?)",
                   (name, phone, new_weight, total))
    conn.commit()

    # Send SMS
    message = f"Dear {name}, you have delivered {new_weight}kg of coffee. Total so far: {total}kg."
    response = sms.send(message, [phone])
    print("SMS sent:", response)

# === EXAMPLE USAGE ===
name = input("Farmer name: ")
phone = input("Phone number (e.g. +2547xxxxxxx): ")
weight = float(input("Weight delivered (kg): "))

record_delivery(name, phone, weight)

