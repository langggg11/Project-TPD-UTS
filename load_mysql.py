# -*- coding: utf-8 -*-
"""
load_mysql.py
Kelompok 8 - Anggota 2: Data Generator & Source Preparation

Fungsi: Load data CSV ke MySQL source database
Tables : drivers, users, locations
Database: gojek_source_mysql

CARA PAKAI:
1. Pastikan MySQL sudah berjalan di localhost:3306
2. Sesuaikan variabel di bagian CONFIG di bawah
3. Jalankan: python load_mysql.py
"""

import pandas as pd
from sqlalchemy import create_engine, text
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ── CONFIG - sesuaikan dengan setup lokal ────────────────────
MYSQL_HOST     = "localhost"
MYSQL_PORT     = 3306
MYSQL_USER     = "root"
MYSQL_PASSWORD = ""           # ganti dengan password MySQL kamu
MYSQL_DATABASE = "gojek_source_mysql"
DATA_DIR       = "data/source"
# ─────────────────────────────────────────────────────────────

print("=" * 55)
print("  LOAD DATA KE MYSQL - Kelompok 8")
print("=" * 55)

# Buat koneksi
try:
    engine = create_engine(
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}",
        echo=False
    )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print(f"\n  [OK] Koneksi ke MySQL berhasil")
    print(f"       Database: {MYSQL_DATABASE} @ {MYSQL_HOST}:{MYSQL_PORT}")
except Exception as e:
    print(f"\n  [ERROR] Gagal konek ke MySQL: {e}")
    print(f"  Pastikan MySQL berjalan dan credential benar di bagian CONFIG")
    sys.exit(1)

# DDL - buat tabel jika belum ada
DDL = {
    "locations": """
        CREATE TABLE IF NOT EXISTS locations (
            location_id   VARCHAR(10)   PRIMARY KEY,
            location_name VARCHAR(100)  NOT NULL,
            city          VARCHAR(50)   NOT NULL,
            province      VARCHAR(50)   NOT NULL,
            latitude      DECIMAL(10,8) NOT NULL,
            longitude     DECIMAL(11,8) NOT NULL,
            zone_type     VARCHAR(20)   NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    "drivers": """
        CREATE TABLE IF NOT EXISTS drivers (
            driver_id     VARCHAR(10)  PRIMARY KEY,
            driver_name   VARCHAR(100) NOT NULL,
            vehicle_type  VARCHAR(20)  NOT NULL,
            license_plate VARCHAR(20)  NOT NULL,
            join_date     DATE         NOT NULL,
            city          VARCHAR(50)  NOT NULL,
            status        VARCHAR(20)  NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            user_id           VARCHAR(12)  PRIMARY KEY,
            user_name         VARCHAR(100) NOT NULL,
            registration_date DATE         NOT NULL,
            user_segment      VARCHAR(20)  NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
}

# Load tiap tabel
files = {
    "locations": "locations.csv",
    "drivers"  : "drivers.csv",
    "users"    : "users.csv",
}

with engine.begin() as conn:
    for table, ddl in DDL.items():
        conn.execute(text(ddl))
        print(f"\n  [OK] Tabel '{table}' siap")

for table, filename in files.items():
    path = f"{DATA_DIR}/{filename}"
    try:
        df = pd.read_csv(path)
        df.to_sql(table, engine, if_exists="replace", index=False, method="multi", chunksize=500)
        print(f"  [OK] Load {filename} -> MySQL.{table} ({len(df):,} rows)")
    except FileNotFoundError:
        print(f"  [ERROR] File tidak ditemukan: {path}")
        print(f"          Jalankan generate_data.py terlebih dahulu!")
    except Exception as e:
        print(f"  [ERROR] Gagal load {table}: {e}")

print(f"\n  [DONE] Load ke MySQL selesai!")
print(f"  Cek di MySQL Workbench: USE {MYSQL_DATABASE};")
print(f"  SELECT COUNT(*) FROM drivers;")
print(f"  SELECT COUNT(*) FROM users;")
print(f"  SELECT COUNT(*) FROM locations;")
print("=" * 55)
