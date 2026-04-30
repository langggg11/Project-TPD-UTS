# -*- coding: utf-8 -*-
"""
load_postgres.py
Kelompok 8 - Anggota 2: Data Generator & Source Preparation

Fungsi: Load data CSV ke PostgreSQL source database
Tables : trips_raw, payments
Database: gojek_source_postgres

CARA PAKAI:
1. Pastikan PostgreSQL sudah berjalan di localhost:5432
2. Buat database dulu: CREATE DATABASE gojek_source_postgres;
3. Sesuaikan variabel CONFIG di bawah
4. Jalankan: python load_postgres.py
"""

import pandas as pd
from sqlalchemy import create_engine, text
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ── CONFIG ────────────────────────────────────────────────────
PG_HOST     = "localhost"
PG_PORT     = 5432
PG_USER     = "postgres"
PG_PASSWORD = ""          # ganti dengan password PostgreSQL kamu
PG_DATABASE = "gojek_source_postgres"
DATA_DIR    = "data/source"
# ─────────────────────────────────────────────────────────────

print("=" * 55)
print("  LOAD DATA KE POSTGRESQL SOURCE - Kelompok 8")
print("=" * 55)

# Buat koneksi
try:
    engine = create_engine(
        f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}",
        echo=False
    )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print(f"\n  [OK] Koneksi ke PostgreSQL berhasil")
    print(f"       Database: {PG_DATABASE} @ {PG_HOST}:{PG_PORT}")
except Exception as e:
    print(f"\n  [ERROR] Gagal konek ke PostgreSQL: {e}")
    print(f"  Pastikan PostgreSQL berjalan dan database sudah dibuat:")
    print(f"  psql -U postgres -c \"CREATE DATABASE {PG_DATABASE};\"")
    sys.exit(1)

# DDL
DDL = {
    "payments": """
        CREATE TABLE IF NOT EXISTS payments (
            payment_id     VARCHAR(10)  PRIMARY KEY,
            payment_method VARCHAR(50)  NOT NULL,
            payment_status VARCHAR(20)  NOT NULL
        );
    """,
    "trips_raw": """
        CREATE TABLE IF NOT EXISTS trips_raw (
            trip_id              VARCHAR(12)    NOT NULL,
            driver_id            VARCHAR(10)    NOT NULL,
            user_id              VARCHAR(12)    NOT NULL,
            pickup_location_id   VARCHAR(10)    NOT NULL,
            dropoff_location_id  VARCHAR(10)    NOT NULL,
            pickup_time          TIMESTAMP      NOT NULL,
            dropoff_time         TIMESTAMP      NOT NULL,
            distance_km          DECIMAL(10,2)  NULL,
            duration_minutes     INT            NULL,
            base_fare            DECIMAL(12,2)  NULL,
            surge_multiplier     DECIMAL(4,2)   NULL,
            trip_status          VARCHAR(30)    NOT NULL,
            payment_method       VARCHAR(50)    NOT NULL,
            payment_status       VARCHAR(20)    NOT NULL
        );
    """,
}

files = {
    "payments" : "payments.csv",
    "trips_raw": "trips_raw.csv",
}

with engine.begin() as conn:
    for table, ddl in DDL.items():
        conn.execute(text(ddl))
        print(f"\n  [OK] Tabel '{table}' siap")

for table, filename in files.items():
    path = f"{DATA_DIR}/{filename}"
    try:
        df = pd.read_csv(path)
        # Drop dulu biar bisa replace (PostgreSQL tidak support if_exists='replace' dgn primary key)
        with engine.begin() as conn:
            conn.execute(text(f"DELETE FROM {table}"))
        df.to_sql(table, engine, if_exists="append", index=False, method="multi", chunksize=500)
        print(f"  [OK] Load {filename} -> PostgreSQL.{table} ({len(df):,} rows)")
    except FileNotFoundError:
        print(f"  [ERROR] File tidak ditemukan: {path}")
        print(f"          Jalankan generate_data.py terlebih dahulu!")
    except Exception as e:
        print(f"  [ERROR] Gagal load {table}: {e}")

print(f"\n  [DONE] Load ke PostgreSQL source selesai!")
print(f"  Cek di psql: \\c {PG_DATABASE}")
print(f"  SELECT COUNT(*) FROM trips_raw;")
print(f"  SELECT COUNT(*) FROM payments;")
print("=" * 55)
