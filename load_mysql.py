"""
load_mysql.py
Load drivers.csv, users.csv, locations.csv ke MySQL container.
Jalankan setelah generate_data.py.

Kebutuhan:
  pip install mysql-connector-python
"""

import csv
import mysql.connector
import os

# ── Konfigurasi koneksi ──────────────────────
MYSQL_CONFIG = {
    "host":     "localhost",
    "port":     3307,          # Host port sesuai docker-compose
    "user":     "root",
    "password": "root",
    "database": "gojek_source_mysql",
}

CSV_DIR = os.path.join("data", "source_csv")


def load_csv(filepath):
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def to_none(val):
    """Konversi empty string ke None (NULL di DB)."""
    if val is None or val == "":
        return None
    return val


def load_drivers(cursor):
    rows = load_csv(os.path.join(CSV_DIR, "drivers.csv"))
    sql  = """
        INSERT INTO drivers
            (driver_id, driver_name, vehicle_type, license_plate,
             join_date, city, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE driver_name = VALUES(driver_name)
    """
    data = [
        (r["driver_id"], r["driver_name"], r["vehicle_type"],
         to_none(r["license_plate"]), to_none(r["join_date"]),
         to_none(r["city"]), r["status"])
        for r in rows
    ]
    cursor.executemany(sql, data)
    print(f"  ✓ drivers    : {len(data):,} rows inserted/updated")


def load_users(cursor):
    rows = load_csv(os.path.join(CSV_DIR, "users.csv"))
    sql  = """
        INSERT INTO users
            (user_id, user_name, registration_date, user_segment)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE user_name = VALUES(user_name)
    """
    data = [
        (r["user_id"], r["user_name"],
         to_none(r["registration_date"]), r["user_segment"])
        for r in rows
    ]
    cursor.executemany(sql, data)
    print(f"  ✓ users      : {len(data):,} rows inserted/updated")


def load_locations(cursor):
    rows = load_csv(os.path.join(CSV_DIR, "locations.csv"))
    sql  = """
        INSERT INTO locations
            (location_id, location_name, city, province,
             latitude, longitude, zone_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE location_name = VALUES(location_name)
    """
    data = [
        (r["location_id"], r["location_name"], r["city"],
         to_none(r["province"]),
         to_none(r["latitude"]), to_none(r["longitude"]),
         to_none(r["zone_type"]))
        for r in rows
    ]
    cursor.executemany(sql, data)
    print(f"  ✓ locations  : {len(data):,} rows inserted/updated")


def main():
    print("=" * 50)
    print("  Load MySQL Source — Gojek DWH")
    print("=" * 50)
    try:
        conn   = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        load_drivers(cursor)
        load_users(cursor)
        load_locations(cursor)
        conn.commit()
        cursor.close()
        conn.close()
        print("\n  ✅  MySQL load selesai!")
    except mysql.connector.Error as e:
        print(f"\n  ❌  Error: {e}")
        raise


if __name__ == "__main__":
    main()
