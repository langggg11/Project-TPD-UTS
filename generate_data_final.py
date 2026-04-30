# -*- coding: utf-8 -*-
"""
=============================================================
  DATA GENERATOR FINAL - Gojek Ride-Hailing Data Warehouse
  Kelompok 8 | Teknologi Perekayasaan Data
  Anggota 2: Data Generator & Source Preparation
=============================================================
  Perubahan dari versi sebelumnya:
  - HAPUS driver_rating dari trips_raw.csv
  - TAMBAH app_events.json untuk MongoDB
  - trip_id di app_events dijamin cocok dengan trips_raw
=============================================================
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
import json
from datetime import datetime, timedelta
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

fake = Faker('id_ID')
Faker.seed(42)
random.seed(42)
np.random.seed(42)

OUTPUT_DIR = "data/source"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("  GOJEK DUMMY DATA GENERATOR FINAL - Kelompok 8")
print("=" * 60)


# ==============================================================
# STEP 1 - locations.csv  (masuk ke MySQL)
# ==============================================================
print("\n[1/6] Generating locations.csv ...")

locations_data = [
    # JAKARTA
    ("Sudirman CBD",        "Jakarta",    "DKI Jakarta",       -6.2088,  106.8456, "Commercial"),
    ("Kuningan",            "Jakarta",    "DKI Jakarta",       -6.2297,  106.8310, "Commercial"),
    ("Blok M",              "Jakarta",    "DKI Jakarta",       -6.2441,  106.7993, "Commercial"),
    ("Kemang",              "Jakarta",    "DKI Jakarta",       -6.2607,  106.8138, "Residential"),
    ("Kelapa Gading",       "Jakarta",    "DKI Jakarta",       -6.1603,  106.9017, "Residential"),
    ("Pluit",               "Jakarta",    "DKI Jakarta",       -6.1208,  106.7936, "Residential"),
    ("Tanjung Priok",       "Jakarta",    "DKI Jakarta",       -6.1080,  106.8755, "Industrial"),
    ("Cengkareng",          "Jakarta",    "DKI Jakarta",       -6.1404,  106.6601, "Industrial"),
    ("Fatmawati",           "Jakarta",    "DKI Jakarta",       -6.2918,  106.7973, "Residential"),
    ("Menteng",             "Jakarta",    "DKI Jakarta",       -6.1968,  106.8318, "Residential"),
    ("Grogol",              "Jakarta",    "DKI Jakarta",       -6.1681,  106.7902, "Commercial"),
    ("Senen",               "Jakarta",    "DKI Jakarta",       -6.1775,  106.8453, "Commercial"),
    # BANDUNG
    ("Dago",                "Bandung",    "Jawa Barat",        -6.8767,  107.6119, "Commercial"),
    ("Buah Batu",           "Bandung",    "Jawa Barat",        -6.9447,  107.6374, "Residential"),
    ("Cihampelas",          "Bandung",    "Jawa Barat",        -6.8976,  107.6028, "Commercial"),
    ("Antapani",            "Bandung",    "Jawa Barat",        -6.9175,  107.6587, "Residential"),
    ("Gedebage",            "Bandung",    "Jawa Barat",        -6.9501,  107.6993, "Industrial"),
    ("Pasteur",             "Bandung",    "Jawa Barat",        -6.8876,  107.5872, "Commercial"),
    # SURABAYA
    ("Gubeng",              "Surabaya",   "Jawa Timur",        -7.2671,  112.7509, "Commercial"),
    ("Rungkut",             "Surabaya",   "Jawa Timur",        -7.3296,  112.7758, "Industrial"),
    ("Darmo",               "Surabaya",   "Jawa Timur",        -7.2840,  112.7282, "Residential"),
    ("Wonokromo",           "Surabaya",   "Jawa Timur",        -7.3034,  112.7357, "Commercial"),
    ("Kenjeran",            "Surabaya",   "Jawa Timur",        -7.2278,  112.7726, "Residential"),
    ("Waru",                "Surabaya",   "Jawa Timur",        -7.3680,  112.7282, "Industrial"),
    # MEDAN
    ("Medan Kota",          "Medan",      "Sumatera Utara",     3.5896,   98.6739, "Commercial"),
    ("Helvetia",            "Medan",      "Sumatera Utara",     3.6227,   98.6390, "Residential"),
    ("Marelan",             "Medan",      "Sumatera Utara",     3.6890,   98.6601, "Industrial"),
    ("Sunggal",             "Medan",      "Sumatera Utara",     3.5712,   98.6271, "Residential"),
    ("Polonia",             "Medan",      "Sumatera Utara",     3.5591,   98.6782, "Commercial"),
    # YOGYAKARTA
    ("Malioboro",           "Yogyakarta", "DI Yogyakarta",     -7.7956,  110.3695, "Commercial"),
    ("Sleman",              "Yogyakarta", "DI Yogyakarta",     -7.7166,  110.3559, "Residential"),
    ("Kotagede",            "Yogyakarta", "DI Yogyakarta",     -7.8306,  110.4032, "Residential"),
    ("Bantul",              "Yogyakarta", "DI Yogyakarta",     -7.8914,  110.3308, "Residential"),
    ("Condongcatur",        "Yogyakarta", "DI Yogyakarta",     -7.7523,  110.3975, "Commercial"),
    # SEMARANG
    ("Simpang Lima",        "Semarang",   "Jawa Tengah",       -6.9932,  110.4204, "Commercial"),
    ("Tembalang",           "Semarang",   "Jawa Tengah",       -7.0516,  110.4376, "Residential"),
    ("Genuk",               "Semarang",   "Jawa Tengah",       -6.9784,  110.4698, "Industrial"),
    ("Banyumanik",          "Semarang",   "Jawa Tengah",       -7.0629,  110.4126, "Residential"),
    # MAKASSAR
    ("Panakkukang",         "Makassar",   "Sulawesi Selatan",  -5.1377,  119.4527, "Commercial"),
    ("Tamalate",            "Makassar",   "Sulawesi Selatan",  -5.1934,  119.4220, "Residential"),
    ("Biringkanaya",        "Makassar",   "Sulawesi Selatan",  -5.0868,  119.5016, "Industrial"),
    # BALI
    ("Kuta",                "Bali",       "Bali",              -8.7215,  115.1685, "Commercial"),
    ("Ubud",                "Bali",       "Bali",              -8.5069,  115.2625, "Residential"),
    ("Denpasar",            "Bali",       "Bali",              -8.6705,  115.2126, "Commercial"),
    ("Seminyak",            "Bali",       "Bali",              -8.6938,  115.1615, "Commercial"),
    ("Nusa Dua",            "Bali",       "Bali",              -8.8008,  115.2320, "Commercial"),
]

df_locations = pd.DataFrame(locations_data,
    columns=["location_name","city","province","latitude","longitude","zone_type"])
df_locations.insert(0, "location_id",
    [f"LOC-{str(i+1).zfill(3)}" for i in range(len(df_locations))])
df_locations.to_csv(f"{OUTPUT_DIR}/locations.csv", index=False)
print(f"   [OK] locations.csv -> {len(df_locations)} rows  (target: MySQL)")


# ==============================================================
# STEP 2 - drivers.csv  (masuk ke MySQL)
# ==============================================================
print("\n[2/6] Generating drivers.csv ...")

CITIES       = ["Jakarta","Bandung","Surabaya","Medan","Yogyakarta","Semarang","Makassar","Bali"]
CITY_WEIGHTS = [0.40, 0.15, 0.15, 0.10, 0.08, 0.05, 0.03, 0.04]

def random_plate(city):
    prefix = {"Jakarta":"B","Bandung":"D","Surabaya":"L",
               "Medan":"BK","Yogyakarta":"AB","Semarang":"H",
               "Makassar":"DD","Bali":"DK"}
    p = prefix.get(city, "B")
    return f"{p} {random.randint(1000,9999)} {fake.lexify('???').upper()}"

drivers = []
for i in range(500):
    city         = random.choices(CITIES, weights=CITY_WEIGHTS, k=1)[0]
    vehicle_type = random.choices(["GoRide","GoCar"], weights=[0.60,0.40])[0]
    join_date    = fake.date_between(start_date="-4y", end_date="-3m")
    status       = random.choices(["Active","Inactive"], weights=[0.85,0.15])[0]
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
print(f"   [OK] drivers.csv -> {len(df_drivers)} rows  (target: MySQL)")


# ==============================================================
# STEP 3 - users.csv  (masuk ke MySQL)
# ==============================================================
print("\n[3/6] Generating users.csv ...")

users = []
for i in range(2000):
    reg_date = fake.date_between(start_date="-3y", end_date="-1m")
    segment  = random.choices(["Regular","VIP"], weights=[0.75,0.25])[0]
    users.append({
        "user_id"          : f"USR-{str(i+1).zfill(6)}",
        "user_name"        : fake.name(),
        "registration_date": reg_date,
        "user_segment"     : segment,
    })

df_users = pd.DataFrame(users)
df_users.to_csv(f"{OUTPUT_DIR}/users.csv", index=False)
print(f"   [OK] users.csv -> {len(df_users)} rows  (target: MySQL)")


# ==============================================================
# STEP 4 - payments.csv  (masuk ke PostgreSQL source)
# ==============================================================
print("\n[4/6] Generating payments.csv ...")

payment_combos = [
    ("GoPay",        "Success"),
    ("GoPay",        "Failed"),
    ("Cash",         "Success"),
    ("Cash",         "Pending"),
    ("Credit Card",  "Success"),
    ("Credit Card",  "Failed"),
]
df_payments = pd.DataFrame(payment_combos, columns=["payment_method","payment_status"])
df_payments.insert(0, "payment_id",
    [f"PAY-{str(i+1).zfill(3)}" for i in range(len(df_payments))])
df_payments.to_csv(f"{OUTPUT_DIR}/payments.csv", index=False)
print(f"   [OK] payments.csv -> {len(df_payments)} rows  (target: PostgreSQL source)")


# ==============================================================
# STEP 5 - trips_raw.csv  (masuk ke PostgreSQL source)
#          TANPA driver_rating
# ==============================================================
print("\n[5/6] Generating trips_raw.csv ...")

driver_ids    = df_drivers["driver_id"].tolist()
driver_cities = dict(zip(df_drivers["driver_id"], df_drivers["city"]))
driver_types  = dict(zip(df_drivers["driver_id"], df_drivers["vehicle_type"]))
user_ids      = df_users["user_id"].tolist()
loc_ids       = df_locations["location_id"].tolist()
loc_by_city   = {}
for _, row in df_locations.iterrows():
    loc_by_city.setdefault(row["city"], []).append(row["location_id"])

payment_methods = ["GoPay","Cash","Credit Card"]
pay_weights     = [0.60, 0.30, 0.10]
pay_status_map  = {
    "GoPay":       [("Success",0.93),("Failed",0.05),("Pending",0.02)],
    "Cash":        [("Success",0.97),("Failed",0.02),("Pending",0.01)],
    "Credit Card": [("Success",0.90),("Failed",0.07),("Pending",0.03)],
}

def random_hour():
    bucket = random.choices(["peak_m","peak_e","offpeak"],
                            weights=[0.25,0.35,0.40])[0]
    if bucket == "peak_m":   return random.choice(range(7,10))
    elif bucket == "peak_e": return random.choice(range(17,21))
    else:
        off = list(range(0,7)) + list(range(10,17)) + list(range(21,24))
        return random.choice(off)

def calc_fare(distance_km, vehicle_type, hour):
    if vehicle_type == "GoRide":
        rate = random.uniform(2000, 4000)
        min_fare = 9000
    else:
        rate = random.uniform(3500, 5500)
        min_fare = 15000
    base = max(min_fare, distance_km * rate)
    base = round(base / 500) * 500
    if hour in range(7,10) or hour in range(17,21):
        surge = round(random.choices([1.0,1.2,1.5,2.0,2.5],
                      weights=[0.30,0.30,0.25,0.10,0.05])[0], 1)
    else:
        surge = round(random.choices([1.0,1.2,1.5],
                      weights=[0.70,0.20,0.10])[0], 1)
    return base, surge

start_date = datetime(2024,1,1)
end_date   = datetime(2024,12,31)
trips      = []

for i in range(10000):
    driver_id    = random.choice(driver_ids)
    driver_city  = driver_cities[driver_id]
    vehicle_type = driver_types[driver_id]
    city_locs    = loc_by_city.get(driver_city, loc_ids)
    pickup_loc   = random.choice(city_locs)
    dropoff_loc  = random.choice(loc_ids) if random.random() < 0.10 \
                   else random.choice(city_locs)

    rand_days    = random.randint(0, (end_date - start_date).days)
    hour         = random_hour()
    pickup_dt    = (start_date + timedelta(days=rand_days)).replace(
                    hour=hour, minute=random.randint(0,59),
                    second=random.randint(0,59))

    distance_km      = round(random.uniform(1.0, 30.0), 2)
    duration_minutes = max(5, int(distance_km * random.uniform(2.5, 6.0)))
    dropoff_dt       = pickup_dt + timedelta(minutes=duration_minutes)
    base_fare, surge = calc_fare(distance_km, vehicle_type, hour)

    trip_status = random.choices(["Completed","Cancelled","Failed"],
                                  weights=[0.85,0.10,0.05])[0]

    pay_method  = random.choices(payment_methods, weights=pay_weights)[0]
    ps, pw      = zip(*pay_status_map[pay_method])
    pay_status  = random.choices(ps, weights=pw)[0]

    trips.append({
        "trip_id"            : f"TRP-{str(i+1).zfill(6)}",
        "driver_id"          : driver_id,
        "user_id"            : random.choice(user_ids),
        "pickup_location_id" : pickup_loc,
        "dropoff_location_id": dropoff_loc,
        "pickup_time"        : pickup_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "dropoff_time"       : dropoff_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "distance_km"        : distance_km,
        "duration_minutes"   : duration_minutes,
        "base_fare"          : base_fare,
        "surge_multiplier"   : surge,
        # TIDAK ADA driver_rating
        "trip_status"        : trip_status,
        "payment_method"     : pay_method,
        "payment_status"     : pay_status,
    })

df_trips = pd.DataFrame(trips)

# Simpan trip_id yang valid untuk dipakai app_events
valid_trip_ids = df_trips["trip_id"].tolist()

# --- Inject noise ---
# A) 200 duplikat trip_id (~2%)
dup = df_trips.sample(n=200, random_state=42)
df_trips = pd.concat([df_trips, dup], ignore_index=True)

# B) Missing distance_km (~3%)
idx = df_trips.sample(frac=0.03, random_state=1).index
df_trips.loc[idx, "distance_km"] = None

# C) Missing base_fare (~2%)
idx = df_trips.sample(frac=0.02, random_state=2).index
df_trips.loc[idx, "base_fare"] = None

# D) Anomali tarif Rp0 & sangat tinggi (~0.5%)
idx = df_trips.sample(frac=0.005, random_state=3).index
half = len(idx) // 2
df_trips.loc[idx[:half], "base_fare"] = 0
df_trips.loc[idx[half:], "base_fare"] = round(random.uniform(500000, 2000000), 0)

# E) Durasi 0 menit (~0.3%)
idx = df_trips.sample(frac=0.003, random_state=4).index
df_trips.loc[idx, "dropoff_time"]    = df_trips.loc[idx, "pickup_time"]
df_trips.loc[idx, "duration_minutes"] = 0

# F) Inconsistent trip_status (~0.5%) - nilai tidak standar
idx = df_trips.sample(frac=0.005, random_state=5).index
bad_status = ["completed","CANCELLED","Cancel","failed","Done"]
df_trips.loc[idx, "trip_status"] = [random.choice(bad_status) for _ in idx]

# G) Invalid surge_multiplier (~0.3%) - nilai di luar range
idx = df_trips.sample(frac=0.003, random_state=6).index
df_trips.loc[idx, "surge_multiplier"] = [
    random.choice([0.0, -1.0, 5.0, 10.0]) for _ in idx
]

df_trips = df_trips.sample(frac=1, random_state=99).reset_index(drop=True)
df_trips.to_csv(f"{OUTPUT_DIR}/trips_raw.csv", index=False)
print(f"   [OK] trips_raw.csv -> {len(df_trips)} rows  (target: PostgreSQL source)")
print(f"        [NOTE] driver_rating sudah DIHAPUS dari file ini")


# ==============================================================
# STEP 6 - app_events.json  (masuk ke MongoDB)
#          trip_id DIJAMIN cocok dengan trips_raw.csv
# ==============================================================
print("\n[6/6] Generating app_events.json ...")

EVENT_SEQUENCE = [
    "booking_created",
    "driver_assigned",
    "pickup_arrived",
    "trip_started",
    "trip_completed",
    "payment_success",
]

# Versi app dan OS
DEVICE_OS      = ["Android","iOS","Android","Android","iOS"]  # Android lebih dominan
APP_VERSIONS   = ["5.1.0","5.2.0","5.2.1","5.3.0","5.3.1","6.0.0"]

# Noise event_type (untuk trip ~10%)
NOISY_TYPES = {
    "booking_created" : ["Booking Created","booking-created","BOOKING_CREATED"],
    "driver_assigned" : ["Driver Assigned","DRIVER_ASSIGNED","driver-assigned"],
    "trip_completed"  : ["Trip Completed","TRIP_COMPLETED","completed"],
    "payment_success" : ["Payment Success","PAYMENT_SUCCESS","payment-success"],
}

events     = []
event_ctr  = 1

# Ambil hanya trip yang Completed untuk event penuh (6 event)
# Trip Cancelled: hanya 2-3 event (booking_created, driver_assigned, satu cancel)
# Trip Failed: hanya 1-2 event

completed_trips  = [t for t in trips if t["trip_status"] == "Completed"]
cancelled_trips  = [t for t in trips if t["trip_status"] == "Cancelled"]
failed_trips     = [t for t in trips if t["trip_status"] == "Failed"]

def add_events(trip_list, event_types, noise_pct=0.10):
    global event_ctr
    for trip in trip_list:
        pickup_dt = datetime.strptime(trip["pickup_time"], "%Y-%m-%d %H:%M:%S")
        device_os      = random.choice(DEVICE_OS)
        app_version    = random.choice(APP_VERSIONS)
        # Beberapa event punya app_version kosong (noise)
        if random.random() < 0.03:
            app_version = None
        # Beberapa device_os kosong (noise)
        if random.random() < 0.02:
            device_os = None

        current_time = pickup_dt - timedelta(minutes=random.randint(1, 5))

        for etype in event_types:
            # Tentukan event_time
            if etype == "booking_created":
                event_time = current_time
            elif etype == "driver_assigned":
                event_time = current_time + timedelta(seconds=random.randint(10,90))
            elif etype == "pickup_arrived":
                event_time = current_time + timedelta(minutes=random.randint(2,8))
            elif etype == "trip_started":
                event_time = current_time + timedelta(minutes=random.randint(3,10))
            elif etype == "trip_completed":
                event_time = datetime.strptime(trip["dropoff_time"], "%Y-%m-%d %H:%M:%S")
            elif etype == "payment_success":
                event_time = datetime.strptime(trip["dropoff_time"], "%Y-%m-%d %H:%M:%S") \
                             + timedelta(seconds=random.randint(5,30))
            else:
                event_time = current_time + timedelta(minutes=1)

            # Tambahkan noise pada event_type (~10%)
            display_type = etype
            if random.random() < noise_pct and etype in NOISY_TYPES:
                display_type = random.choice(NOISY_TYPES[etype])

            # Missing event_time (~1%)
            evt_time_str = event_time.strftime("%Y-%m-%d %H:%M:%S") \
                           if random.random() > 0.01 else None

            events.append({
                "event_id"   : f"EVT-{str(event_ctr).zfill(7)}",
                "trip_id"    : trip["trip_id"],
                "user_id"    : trip["user_id"],
                "event_type" : display_type,
                "event_time" : evt_time_str,
                "device_os"  : device_os,
                "app_version": app_version,
            })
            event_ctr += 1

# Completed: semua 6 event
add_events(completed_trips, EVENT_SEQUENCE, noise_pct=0.10)

# Cancelled: hanya 2 event (booking_created + driver_assigned)
add_events(cancelled_trips, ["booking_created","driver_assigned"], noise_pct=0.05)

# Failed: hanya 1 event (booking_created)
add_events(failed_trips, ["booking_created"], noise_pct=0.05)

# --- Tambah duplikat event_id (~1%) ---
dup_count = int(len(events) * 0.01)
dup_events = random.choices(events, k=dup_count)
events.extend(dup_events)
random.shuffle(events)

# Simpan ke JSON
with open(f"{OUTPUT_DIR}/app_events.json", "w", encoding="utf-8") as f:
    json.dump(events, f, ensure_ascii=False, indent=2, default=str)

print(f"   [OK] app_events.json -> {len(events)} events  (target: MongoDB)")
print(f"        - trip_id cocok dengan trips_raw: DIJAMIN")
print(f"        - noise: inconsistent event_type, missing event_time/app_version/device_os, duplikat")


# ==============================================================
# SUMMARY
# ==============================================================
print("\n" + "=" * 60)
print("  SUMMARY FINAL")
print("=" * 60)

total = len(df_locations)+len(df_drivers)+len(df_users)+len(df_payments)+len(df_trips)+len(events)
print(f"\n  File                  Rows/Events   Target DB")
print(f"  --------------------  ------------  -------------------")
print(f"  locations.csv         {len(df_locations):>6,}        MySQL")
print(f"  drivers.csv           {len(df_drivers):>6,}        MySQL")
print(f"  users.csv             {len(df_users):>6,}        MySQL")
print(f"  payments.csv          {len(df_payments):>6,}        PostgreSQL source")
print(f"  trips_raw.csv         {len(df_trips):>6,}        PostgreSQL source")
print(f"  app_events.json       {len(events):>6,}        MongoDB")
print(f"  --------------------  ------------")
print(f"  TOTAL                 {total:>6,}")

print(f"\n  trips_raw.csv quality issues:")
print(f"    Missing distance_km       : {df_trips['distance_km'].isna().sum()}")
print(f"    Missing base_fare         : {df_trips['base_fare'].isna().sum()}")
print(f"    Duplikat trip_id          : {df_trips.duplicated('trip_id').sum()}")
print(f"    Duration = 0              : {(df_trips['duration_minutes']==0).sum()}")
print(f"    Base fare = 0             : {(df_trips['base_fare']==0).sum()}")
print(f"    Inconsistent trip_status  : ~50 rows")
print(f"    Invalid surge_multiplier  : ~30 rows")
print(f"    driver_rating             : DIHAPUS")

print(f"\n  app_events.json quality issues:")
print(f"    Inconsistent event_type   : ~10% dari event")
print(f"    Missing event_time        : ~1% dari event")
print(f"    Missing app_version       : ~3% dari event")
print(f"    Missing device_os         : ~2% dari event")
print(f"    Duplikat event_id         : ~1% dari event")

print(f"\n  [DONE] Semua file tersimpan di folder: {OUTPUT_DIR}/")
print("=" * 60)