# -*- coding: utf-8 -*-
"""
=============================================================
  DATA GENERATOR - Gojek Ride-Hailing Data Warehouse
  Kelompok 8 | Teknologi Perekayasaan Data
  Anggota 2: Data Generator & Source Preparation
=============================================================

Output files:
  - locations.csv   (~50 rows)    : Master data lokasi
  - drivers.csv     (~500 rows)   : Master data driver
  - users.csv       (~2000 rows)  : Master data pengguna
  - payments.csv    (~6 rows)     : Referensi metode & status pembayaran
  - trips_raw.csv   (~10000 rows) : Data transaksi mentah (ada noise)
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os
import sys

# Fix encoding untuk Windows (supaya tidak UnicodeEncodeError)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ── Setup ──────────────────────────────────────────────────
fake = Faker('id_ID')
Faker.seed(42)
random.seed(42)
np.random.seed(42)

OUTPUT_DIR = "data/source"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("  GOJEK DUMMY DATA GENERATOR - Kelompok 8")
print("=" * 60)


# ==============================================================
# STEP 1 — locations.csv
# Referensi lokasi nyata di kota-kota Indonesia
# Dipakai sebagai pickup & dropoff di trips_raw
# ==============================================================
print("\n[1/5] Generating locations.csv ...")

locations_data = [
    # ── JAKARTA ──
    ("Sudirman CBD",        "Jakarta", "DKI Jakarta", -6.2088,  106.8456, "Commercial"),
    ("Kuningan",            "Jakarta", "DKI Jakarta", -6.2297,  106.8310, "Commercial"),
    ("Blok M",              "Jakarta", "DKI Jakarta", -6.2441,  106.7993, "Commercial"),
    ("Kemang",              "Jakarta", "DKI Jakarta", -6.2607,  106.8138, "Residential"),
    ("Kelapa Gading",       "Jakarta", "DKI Jakarta", -6.1603,  106.9017, "Residential"),
    ("Pluit",               "Jakarta", "DKI Jakarta", -6.1208,  106.7936, "Residential"),
    ("Tanjung Priok",       "Jakarta", "DKI Jakarta", -6.1080,  106.8755, "Industrial"),
    ("Cengkareng",          "Jakarta", "DKI Jakarta", -6.1404,  106.6601, "Industrial"),
    ("Fatmawati",           "Jakarta", "DKI Jakarta", -6.2918,  106.7973, "Residential"),
    ("Menteng",             "Jakarta", "DKI Jakarta", -6.1968,  106.8318, "Residential"),
    ("Grogol",              "Jakarta", "DKI Jakarta", -6.1681,  106.7902, "Commercial"),
    ("Senen",               "Jakarta", "DKI Jakarta", -6.1775,  106.8453, "Commercial"),
    # ── BANDUNG ──
    ("Dago",                "Bandung", "Jawa Barat",  -6.8767,  107.6119, "Commercial"),
    ("Buah Batu",           "Bandung", "Jawa Barat",  -6.9447,  107.6374, "Residential"),
    ("Cihampelas",          "Bandung", "Jawa Barat",  -6.8976,  107.6028, "Commercial"),
    ("Antapani",            "Bandung", "Jawa Barat",  -6.9175,  107.6587, "Residential"),
    ("Gedebage",            "Bandung", "Jawa Barat",  -6.9501,  107.6993, "Industrial"),
    ("Pasteur",             "Bandung", "Jawa Barat",  -6.8876,  107.5872, "Commercial"),
    # ── SURABAYA ──
    ("Gubeng",              "Surabaya", "Jawa Timur", -7.2671,  112.7509, "Commercial"),
    ("Rungkut",             "Surabaya", "Jawa Timur", -7.3296,  112.7758, "Industrial"),
    ("Darmo",               "Surabaya", "Jawa Timur", -7.2840,  112.7282, "Residential"),
    ("Wonokromo",           "Surabaya", "Jawa Timur", -7.3034,  112.7357, "Commercial"),
    ("Kenjeran",            "Surabaya", "Jawa Timur", -7.2278,  112.7726, "Residential"),
    ("Waru",                "Surabaya", "Jawa Timur", -7.3680,  112.7282, "Industrial"),
    # ── MEDAN ──
    ("Medan Kota",          "Medan", "Sumatera Utara", 3.5896, 98.6739, "Commercial"),
    ("Helvetia",            "Medan", "Sumatera Utara", 3.6227, 98.6390, "Residential"),
    ("Marelan",             "Medan", "Sumatera Utara", 3.6890, 98.6601, "Industrial"),
    ("Sunggal",             "Medan", "Sumatera Utara", 3.5712, 98.6271, "Residential"),
    ("Polonia",             "Medan", "Sumatera Utara", 3.5591, 98.6782, "Commercial"),
    # ── YOGYAKARTA ──
    ("Malioboro",           "Yogyakarta", "DI Yogyakarta", -7.7956, 110.3695, "Commercial"),
    ("Sleman",              "Yogyakarta", "DI Yogyakarta", -7.7166, 110.3559, "Residential"),
    ("Kotagede",            "Yogyakarta", "DI Yogyakarta", -7.8306, 110.4032, "Residential"),
    ("Bantul",              "Yogyakarta", "DI Yogyakarta", -7.8914, 110.3308, "Residential"),
    ("Condongcatur",        "Yogyakarta", "DI Yogyakarta", -7.7523, 110.3975, "Commercial"),
    # ── SEMARANG ──
    ("Simpang Lima",        "Semarang", "Jawa Tengah",  -6.9932, 110.4204, "Commercial"),
    ("Tembalang",           "Semarang", "Jawa Tengah",  -7.0516, 110.4376, "Residential"),
    ("Genuk",               "Semarang", "Jawa Tengah",  -6.9784, 110.4698, "Industrial"),
    ("Banyumanik",          "Semarang", "Jawa Tengah",  -7.0629, 110.4126, "Residential"),
    # ── MAKASSAR ──
    ("Panakkukang",         "Makassar", "Sulawesi Selatan", -5.1377, 119.4527, "Commercial"),
    ("Tamalate",            "Makassar", "Sulawesi Selatan", -5.1934, 119.4220, "Residential"),
    ("Biringkanaya",        "Makassar", "Sulawesi Selatan", -5.0868, 119.5016, "Industrial"),
    # ── BALI ──
    ("Kuta",                "Bali", "Bali",           -8.7215, 115.1685, "Commercial"),
    ("Ubud",                "Bali", "Bali",           -8.5069, 115.2625, "Residential"),
    ("Denpasar",            "Bali", "Bali",           -8.6705, 115.2126, "Commercial"),
    ("Seminyak",            "Bali", "Bali",           -8.6938, 115.1615, "Commercial"),
    ("Nusa Dua",            "Bali", "Bali",           -8.8008, 115.2320, "Commercial"),
]

df_locations = pd.DataFrame(locations_data, columns=[
    "location_name", "city", "province", "latitude", "longitude", "zone_type"
])
# location_id sebagai business key (untuk trips_raw nanti)
df_locations.insert(0, "location_id", [f"LOC-{str(i+1).zfill(3)}" for i in range(len(df_locations))])

df_locations.to_csv(f"{OUTPUT_DIR}/locations.csv", index=False)
print(f"   [OK] locations.csv -> {len(df_locations)} rows")


# ==============================================================
# STEP 2 — drivers.csv
# ~500 driver, tersebar di berbagai kota
# ==============================================================
print("\n[2/5] Generating drivers.csv ...")

CITIES        = df_locations["city"].unique().tolist()
CITY_WEIGHTS  = [0.40, 0.15, 0.15, 0.10, 0.08, 0.05, 0.03, 0.04]  # sesuai urutan CITIES

def random_plate(city):
    """Generate plat nomor realistis per kota."""
    prefix = {
        "Jakarta": "B", "Bandung": "D", "Surabaya": "L",
        "Medan": "BK", "Yogyakarta": "AB", "Semarang": "H",
        "Makassar": "DD", "Bali": "DK"
    }
    p = prefix.get(city, "B")
    return f"{p} {random.randint(1000,9999)} {fake.lexify('???').upper()}"

drivers = []
for i in range(500):
    city         = random.choices(CITIES, weights=CITY_WEIGHTS, k=1)[0]
    vehicle_type = random.choices(["GoRide", "GoCar"], weights=[0.60, 0.40])[0]
    join_date    = fake.date_between(start_date="-4y", end_date="-3m")
    status       = random.choices(["Active", "Inactive"], weights=[0.85, 0.15])[0]

    drivers.append({
        "driver_id"    : f"DRV-{str(i+1).zfill(5)}",
        "driver_name"  : fake.name(),
        "vehicle_type" : vehicle_type,
        "license_plate": random_plate(city),
        "join_date"    : join_date,
        "city"         : city,
        "status"       : status,
    })

df_drivers = pd.DataFrame(drivers)
df_drivers.to_csv(f"{OUTPUT_DIR}/drivers.csv", index=False)
print(f"   [OK] drivers.csv -> {len(df_drivers)} rows")


# ==============================================================
# STEP 3 — users.csv
# ~2000 pengguna
# ==============================================================
print("\n[3/5] Generating users.csv ...")

users = []
for i in range(2000):
    reg_date = fake.date_between(start_date="-3y", end_date="-1m")
    segment  = random.choices(["Regular", "VIP"], weights=[0.75, 0.25])[0]

    users.append({
        "user_id"          : f"USR-{str(i+1).zfill(6)}",
        "user_name"        : fake.name(),
        "registration_date": reg_date,
        "user_segment"     : segment,
    })

df_users = pd.DataFrame(users)
df_users.to_csv(f"{OUTPUT_DIR}/users.csv", index=False)
print(f"   [OK] users.csv -> {len(df_users)} rows")


# ==============================================================
# STEP 4 — payments.csv
# Hanya ~6 baris: kombinasi metode × status
# (sesuai data dictionary terbaru)
# ==============================================================
print("\n[4/5] Generating payments.csv ...")

payment_combos = [
    ("GoPay",       "Success"),
    ("GoPay",       "Failed"),
    ("Cash",        "Success"),
    ("Cash",        "Pending"),
    ("Credit Card", "Success"),
    ("Credit Card", "Failed"),
]

df_payments = pd.DataFrame(payment_combos, columns=["payment_method", "payment_status"])
df_payments.insert(0, "payment_id", [f"PAY-{str(i+1).zfill(3)}" for i in range(len(df_payments))])
df_payments.to_csv(f"{OUTPUT_DIR}/payments.csv", index=False)
print(f"   [OK] payments.csv -> {len(df_payments)} rows")


# ==============================================================
# STEP 5 — trips_raw.csv
# ~10.000 baris data transaksi MENTAH
# Sengaja ada: missing values, duplikasi, anomali
# ==============================================================
print("\n[5/5] Generating trips_raw.csv ...")

driver_ids   = df_drivers["driver_id"].tolist()
driver_cities = dict(zip(df_drivers["driver_id"], df_drivers["city"]))
user_ids     = df_users["user_id"].tolist()
loc_ids      = df_locations["location_id"].tolist()
loc_cities   = dict(zip(df_locations["location_id"], df_locations["city"]))

# Distribusi kota untuk trip (Jakarta paling dominan)
loc_by_city = {}
for _, row in df_locations.iterrows():
    loc_by_city.setdefault(row["city"], []).append(row["location_id"])

payment_methods = ["GoPay", "Cash", "Credit Card"]
pay_weights     = [0.60, 0.30, 0.10]
pay_status_map  = {
    "GoPay":       [("Success", 0.93), ("Failed", 0.05), ("Pending", 0.02)],
    "Cash":        [("Success", 0.97), ("Failed", 0.02), ("Pending", 0.01)],
    "Credit Card": [("Success", 0.90), ("Failed", 0.07), ("Pending", 0.03)],
}

def random_hour():
    """Distribusi jam lebih banyak di peak hours (pagi & sore)."""
    peak_morning = list(range(7, 10))    # 07-09
    peak_evening = list(range(17, 21))   # 17-20
    offpeak      = list(range(0, 7)) + list(range(10, 17)) + list(range(21, 24))
    bucket = random.choices(["peak_m", "peak_e", "offpeak"],
                            weights=[0.25, 0.35, 0.40])[0]
    if bucket == "peak_m":   return random.choice(peak_morning)
    elif bucket == "peak_e": return random.choice(peak_evening)
    else:                    return random.choice(offpeak)

def calc_fare(distance_km, vehicle_type, hour):
    """Hitung tarif realistis berdasarkan jarak & tipe kendaraan."""
    if vehicle_type == "GoRide":
        rate_per_km = random.uniform(2000, 4000)
        min_fare    = 9000
    else:  # GoCar
        rate_per_km = random.uniform(3500, 5500)
        min_fare    = 15000

    base = max(min_fare, distance_km * rate_per_km)
    base = round(base / 500) * 500  # bulatkan ke 500

    # Surge multiplier: lebih tinggi di peak hours
    if hour in range(7, 10) or hour in range(17, 21):
        surge = round(random.choices(
            [1.0, 1.2, 1.5, 2.0, 2.5],
            weights=[0.30, 0.30, 0.25, 0.10, 0.05])[0], 1)
    else:
        surge = round(random.choices(
            [1.0, 1.2, 1.5],
            weights=[0.70, 0.20, 0.10])[0], 1)

    return base, surge

trips = []
start_date = datetime(2024, 1, 1)
end_date   = datetime(2024, 12, 31)

for i in range(10000):
    # Pilih driver -> ambil kota driver -> cari lokasi di kota yang sama
    driver_id   = random.choice(driver_ids)
    driver_city = driver_cities[driver_id]
    vehicle_type = df_drivers[df_drivers["driver_id"] == driver_id]["vehicle_type"].values[0]

    city_locs = loc_by_city.get(driver_city, loc_ids)
    pickup_loc  = random.choice(city_locs)
    # Dropoff bisa beda kota (trip lintas kota, ~10%)
    if random.random() < 0.10:
        dropoff_loc = random.choice(loc_ids)
    else:
        dropoff_loc = random.choice(city_locs)

    # Waktu perjalanan
    rand_days   = random.randint(0, (end_date - start_date).days)
    pickup_dt   = start_date + timedelta(days=rand_days)
    hour        = random_hour()
    minute      = random.randint(0, 59)
    pickup_dt   = pickup_dt.replace(hour=hour, minute=minute, second=random.randint(0, 59))

    # Durasi & jarak
    distance_km      = round(random.uniform(1.0, 30.0), 2)
    duration_minutes = max(5, int(distance_km * random.uniform(2.5, 6.0)))
    dropoff_dt       = pickup_dt + timedelta(minutes=duration_minutes)

    # Tarif
    base_fare, surge = calc_fare(distance_km, vehicle_type, hour)

    # Trip status
    trip_status = random.choices(
        ["Completed", "Cancelled", "Failed"],
        weights=[0.85, 0.10, 0.05])[0]

    # Rating hanya untuk trip Completed
    if trip_status == "Completed":
        driver_rating = round(random.choices(
            [3.0, 3.5, 4.0, 4.5, 5.0],
            weights=[0.03, 0.07, 0.20, 0.35, 0.35])[0], 1)
    else:
        driver_rating = None  # missing value alami

    # Pembayaran
    pay_method = random.choices(payment_methods, weights=pay_weights)[0]
    pay_statuses, pay_weights_inner = zip(*pay_status_map[pay_method])
    pay_status = random.choices(pay_statuses, weights=pay_weights_inner)[0]

    trips.append({
        "trip_id"         : f"TRP-{str(i+1).zfill(6)}",
        "driver_id"       : driver_id,
        "user_id"         : random.choice(user_ids),
        "pickup_location_id" : pickup_loc,
        "dropoff_location_id": dropoff_loc,
        "pickup_time"     : pickup_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "dropoff_time"    : dropoff_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "distance_km"     : distance_km,
        "duration_minutes": duration_minutes,
        "base_fare"       : base_fare,
        "surge_multiplier": surge,
        "driver_rating"   : driver_rating,
        "trip_status"     : trip_status,
        "payment_method"  : pay_method,
        "payment_status"  : pay_status,
    })

df_trips = pd.DataFrame(trips)

# ── Inject noise (data kotor yang realistis) ──────────────────

# A) Tambahkan ~200 duplikat trip_id (2%)
dup_indices = df_trips.sample(n=200, random_state=42).index
df_dups     = df_trips.loc[dup_indices].copy()
df_trips    = pd.concat([df_trips, df_dups], ignore_index=True)

# B) Missing values tambahan pada beberapa kolom (~3-5%)
miss_idx_dist = df_trips.sample(frac=0.03, random_state=1).index
df_trips.loc[miss_idx_dist, "distance_km"] = None

miss_idx_fare = df_trips.sample(frac=0.02, random_state=2).index
df_trips.loc[miss_idx_fare, "base_fare"] = None

# C) Anomali tarif (0 atau sangat tinggi, ~0.5%)
anomaly_idx = df_trips.sample(frac=0.005, random_state=3).index
df_trips.loc[anomaly_idx[:len(anomaly_idx)//2], "base_fare"] = 0
df_trips.loc[anomaly_idx[len(anomaly_idx)//2:], "base_fare"] = random.uniform(500000, 2000000)

# D) Anomali durasi 0 menit (~0.3%)
zero_dur_idx = df_trips.sample(frac=0.003, random_state=4).index
df_trips.loc[zero_dur_idx, "dropoff_time"] = df_trips.loc[zero_dur_idx, "pickup_time"]
df_trips.loc[zero_dur_idx, "duration_minutes"] = 0

# Shuffle agar duplikat tidak berurutan
df_trips = df_trips.sample(frac=1, random_state=99).reset_index(drop=True)

df_trips.to_csv(f"{OUTPUT_DIR}/trips_raw.csv", index=False)
print(f"   [OK] trips_raw.csv -> {len(df_trips)} rows (termasuk noise)")


# ==============================================================
# SUMMARY REPORT
# ==============================================================
print("\n" + "=" * 60)
print("  SUMMARY REPORT")
print("=" * 60)

total_rows = len(df_locations) + len(df_drivers) + len(df_users) + len(df_payments) + len(df_trips)

print(f"\n  File                Rows")
print(f"  ------------------  --------")
print(f"  locations.csv       {len(df_locations):>8,}")
print(f"  drivers.csv         {len(df_drivers):>8,}")
print(f"  users.csv           {len(df_users):>8,}")
print(f"  payments.csv        {len(df_payments):>8,}")
print(f"  trips_raw.csv       {len(df_trips):>8,}")
print(f"  ------------------  --------")
print(f"  TOTAL               {total_rows:>8,}")

print(f"\n   trips_raw.csv Stats:")
print(f"     Trip Status     : {df_trips['trip_status'].value_counts().to_dict()}")
print(f"     Payment Method  : {df_trips['payment_method'].value_counts().to_dict()}")
print(f"     Missing rating  : {df_trips['driver_rating'].isna().sum()} rows")
print(f"     Missing distance: {df_trips['distance_km'].isna().sum()} rows")
print(f"     Duplikat trip_id: {df_trips.duplicated('trip_id').sum()} rows")
print(f"     Zero duration   : {(df_trips['duration_minutes'] == 0).sum()} rows")
print(f"     Zero fare anomaly: {(df_trips['base_fare'] == 0).sum()} rows")

print(f"\n  [DONE] Semua file tersimpan di folder: {OUTPUT_DIR}/")
print("=" * 60)