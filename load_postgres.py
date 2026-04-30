"""
load_postgres.py
Load trips_raw.csv dan payments.csv ke PostgreSQL Source container.
Jalankan setelah generate_data.py.

Kebutuhan:
  pip install psycopg2-binary
"""

import csv
import psycopg2
import os

# ── Konfigurasi koneksi ──────────────────────
PG_CONFIG = {
    "host":     "localhost",
    "port":     5434,          # Host port sesuai docker-compose
    "user":     "postgres",
    "password": "postgres",
    "dbname":   "gojek_source_postgres",
}

CSV_DIR = os.path.join("data", "source_csv")


def load_csv(filepath):
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def to_none(val):
    if val is None or val == "" or val == "None":
        return None
    return val


def to_decimal(val):
    v = to_none(val)
    if v is None:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def to_int(val):
    v = to_none(val)
    if v is None:
        return None
    try:
        return int(float(v))
    except ValueError:
        return None


def load_trips_raw(cursor):
    rows = load_csv(os.path.join(CSV_DIR, "trips_raw.csv"))
    sql  = """
        INSERT INTO trips_raw
            (trip_id, driver_id, user_id,
             pickup_location_id, dropoff_location_id,
             pickup_time, dropoff_time,
             distance_km, duration_minutes,
             base_fare, surge_multiplier, total_fare,
             trip_status, payment_method, payment_status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    # Catatan: raw_trip_id adalah SERIAL — tidak perlu di-insert manual
    data = [
        (r["trip_id"], r["driver_id"], r["user_id"],
         r["pickup_location_id"], r["dropoff_location_id"],
         to_none(r["pickup_time"]), to_none(r["dropoff_time"]),
         to_decimal(r["distance_km"]), to_int(r["duration_minutes"]),
         to_decimal(r["base_fare"]), to_decimal(r["surge_multiplier"]),
         to_decimal(r["total_fare"]),
         r["trip_status"],
         to_none(r["payment_method"]), to_none(r["payment_status"]))
        for r in rows
    ]
    cursor.executemany(sql, data)
    print(f"  ✓ trips_raw  : {len(data):,} rows inserted")


def load_payments(cursor):
    rows = load_csv(os.path.join(CSV_DIR, "payments.csv"))
    # Truncate dulu agar bisa di-reload berulang kali
    cursor.execute("TRUNCATE TABLE payments RESTART IDENTITY CASCADE")
    sql  = """
        INSERT INTO payments (trip_id, payment_method, payment_status)
        VALUES (%s, %s, %s)
    """
    data = [
        (r["trip_id"], r["payment_method"], r["payment_status"])
        for r in rows
    ]
    cursor.executemany(sql, data)
    print(f"  ✓ payments   : {len(data):,} rows inserted")


def main():
    print("=" * 50)
    print("  Load PostgreSQL Source — Gojek DWH")
    print("=" * 50)
    try:
        conn   = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        load_trips_raw(cursor)
        load_payments(cursor)
        conn.commit()
        cursor.close()
        conn.close()
        print("\n  ✅  PostgreSQL load selesai!")
    except psycopg2.Error as e:
        print(f"\n  ❌  Error: {e}")
        raise


if __name__ == "__main__":
    main()
