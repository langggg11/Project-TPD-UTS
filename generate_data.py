"""
=============================================================
generate_data.py
Proyek  : Data Warehouse & ETL Pipeline - Ride-Hailing Gojek
Orang   : Anggota 2 - Data Engineer (Data Generation)
Output  : drivers.csv, users.csv, locations.csv,
          trips_raw.csv, payments.csv, app_events.json
=============================================================

Data yang dihasilkan:
  - 500  drivers  (MySQL.drivers)
  - 2000 users    (MySQL.users)
  - 57   locations (MySQL.locations)
  - 6000 trips    (PostgreSQL.trips_raw)  -> ~6.300 termasuk noise DQ duplikat
  - 6000 payments (PostgreSQL.payments)
  - ~34000 app_events (MongoDB)           -> ~5-6 event per trip + noise DQ

Data Quality Issues yang sengaja disisipkan (sesuai project plan):
  trips_raw  : duplicate trip_id, NULL distance_km, NULL base_fare,
               duration_minutes <= 0, base_fare = 0, surge_multiplier invalid,
               trip_status tidak konsisten
  app_events : duplicate event_id, NULL event_time,
               event_type format tidak konsisten, NULL app_version/device_os
=============================================================
"""

import random
import json
import csv
import os
from datetime import datetime, timedelta, date

# ----------------------------------------────────────────────────────────────────────
# SEED & CONFIG
# ----------------------------------------────────────────────────────────────────────
random.seed(42)

OUTPUT_DIR = "data"
CSV_DIR    = os.path.join(OUTPUT_DIR, "source_csv")
JSON_DIR   = os.path.join(OUTPUT_DIR, "source_json")

os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)

# ----------------------------------------────────────────────────────────────────────
# REFERENCE DATA
# ----------------------------------------────────────────────────────────────────────
CITIES = [
    "Jakarta", "Surabaya", "Bandung", "Medan",
    "Semarang", "Makassar", "Yogyakarta", "Palembang"
]

CITY_PROVINCE = {
    "Jakarta":    ("DKI Jakarta",       -6.2088,   106.8456),
    "Surabaya":   ("Jawa Timur",        -7.2575,   112.7521),
    "Bandung":    ("Jawa Barat",        -6.9175,   107.6191),
    "Medan":      ("Sumatera Utara",    3.5952,    98.6722),
    "Semarang":   ("Jawa Tengah",       -6.9932,   110.4203),
    "Makassar":   ("Sulawesi Selatan",  -5.1477,   119.4327),
    "Yogyakarta": ("DI Yogyakarta",     -7.7971,   110.3688),
    "Palembang":  ("Sumatera Selatan",  -2.9761,   104.7754),
}

ZONE_TYPES = ["Residential", "Commercial", "Industrial"]

VEHICLE_TYPES   = ["GoRide", "GoCar"]
USER_SEGMENTS   = ["Regular", "VIP"]
DRIVER_STATUSES = ["Active", "Inactive"]

PAYMENT_METHODS  = ["GoPay", "Cash", "Credit Card"]
PAYMENT_STATUSES = ["Success", "Failed", "Pending"]
TRIP_STATUSES    = ["Completed", "Cancelled", "Failed"]

DEVICE_OS_LIST   = ["Android", "iOS"]
APP_VERSIONS     = ["5.0.0", "5.1.0", "5.2.0", "5.2.1", "5.3.0", "6.0.0"]

EVENT_TYPES_ORDERED = [
    "booking_created",
    "driver_assigned",
    "pickup_arrived",
    "trip_started",
    "trip_completed",
    "payment_success",
]

# Indonesian name parts
FIRST_NAMES = [
    "Andi","Budi","Citra","Dewi","Eko","Fitri","Galih","Hendra",
    "Indah","Joko","Kartika","Lina","Made","Nanda","Oki","Putri",
    "Reza","Sari","Tono","Ulfa","Vika","Wahyu","Xena","Yogi","Zahra",
    "Agus","Bambang","Cahaya","Dian","Fauzi","Gunawan","Hadi","Irfan",
    "Jaya","Krisna","Lestari","Mulia","Niko","Oscar","Pandu","Ratna",
    "Surya","Tari","Usman","Vera","Wendi","Yanti","Zulfa","Aditya",
]
LAST_NAMES = [
    "Santoso","Wijaya","Kusuma","Pratama","Suwandi","Hidayat","Nugroho",
    "Saputra","Wibowo","Handoko","Rahayu","Sugiarto","Permata","Halim",
    "Saputro","Gunawan","Wahyudi","Kurniawan","Setiawan","Putra",
]

LOCATION_NAMES_BY_CITY = {
    "Jakarta":    ["Sudirman","Thamrin","Kuningan","Menteng","Kemang","Blok M",
                   "Senayan","Kelapa Gading","Cibubur","Pluit","Grogol","Cawang"],
    "Surabaya":   ["Gubeng","Darmo","Kenjeran","Semampir","Wonokromo","Genteng",
                   "Mulyorejo","Benowo","Wiyung","Tambaksari"],
    "Bandung":    ["Dago","Buah Batu","Cimahi","Antapani","Cicendo","Coblong",
                   "Regol","Sukajadi","Mandalajati"],
    "Medan":      ["Helvetia","Medan Kota","Polonia","Sunggal","Tembung","Selayang"],
    "Semarang":   ["Simpang Lima","Banyumanik","Gajahmungkur","Tembalang","Ngaliyan"],
    "Makassar":   ["Panakkukang","Tamalate","Rappocini","Biringkanaya","Manggala"],
    "Yogyakarta": ["Malioboro","Kotagede","Gondokusuman","Umbulharjo","Sleman"],
    "Palembang":  ["Ilir Barat","Ilir Timur","Seberang Ulu","Bukit Kecil","Kalidoni"],
}

PLATE_LETTERS = {
    "Jakarta": "B", "Surabaya": "L", "Bandung": "D",
    "Medan": "BK", "Semarang": "H", "Makassar": "DD",
    "Yogyakarta": "AB", "Palembang": "BG",
}

# ----------------------------------------────────────────────────────────────────────
# HELPER FUNCTIONS
# ----------------------------------------────────────────────────────────────────────

def rand_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def rand_date(start_year=2018, end_year=2023):
    start = date(start_year, 1, 1)
    end   = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def rand_datetime(start="2024-01-01", end="2024-12-31"):
    fmt   = "%Y-%m-%d"
    start_dt = datetime.strptime(start, fmt)
    end_dt   = datetime.strptime(end, fmt)
    delta    = int((end_dt - start_dt).total_seconds())
    return start_dt + timedelta(seconds=random.randint(0, delta))

def fmt_ts(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def rand_lat_lon(city):
    base_lat, base_lon = CITY_PROVINCE[city][1], CITY_PROVINCE[city][2]
    lat = round(base_lat + random.uniform(-0.1, 0.1), 8)
    lon = round(base_lon + random.uniform(-0.1, 0.1), 8)
    return lat, lon

def write_csv(filepath, fieldnames, rows):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  [OK] {os.path.basename(filepath):30s}  ({len(rows):,} rows)")

# ----------------------------------------────────────────────────────────────────────
# 1. GENERATE drivers.csv  (MySQL.drivers)
# ----------------------------------------────────────────────────────────────────────

def generate_drivers(n=200):
    rows = []
    for i in range(1, n + 1):
        city = random.choice(CITIES)
        vtype = random.choice(VEHICLE_TYPES)
        prefix = PLATE_LETTERS.get(city, "B")
        # Beberapa license_plate NULL (data quality)
        plate = f"{prefix} {random.randint(1000,9999)} {random.choice('ABCDEFGH')}{random.choice('ABCDEFGH')}" \
                if random.random() > 0.05 else None
        join_dt = rand_date(2018, 2023) if random.random() > 0.03 else None
        status  = random.choices(DRIVER_STATUSES, weights=[85, 15])[0]
        rows.append({
            "driver_id":     f"DRV-{i:05d}",
            "driver_name":   rand_name(),
            "vehicle_type":  vtype,
            "license_plate": plate,
            "join_date":     join_dt,
            "city":          city,
            "status":        status,
        })
    filepath = os.path.join(CSV_DIR, "drivers.csv")
    write_csv(filepath, ["driver_id","driver_name","vehicle_type",
                         "license_plate","join_date","city","status"], rows)
    return [r["driver_id"] for r in rows], \
           {r["driver_id"]: r["city"] for r in rows}

# ----------------------------------------────────────────────────────────────────────
# 2. GENERATE users.csv  (MySQL.users)
# ----------------------------------------────────────────────────────────────────────

def generate_users(n=500):
    rows = []
    for i in range(1, n + 1):
        reg_dt  = rand_date(2019, 2024) if random.random() > 0.02 else None
        segment = random.choices(USER_SEGMENTS, weights=[80, 20])[0]
        rows.append({
            "user_id":           f"USR-{i:05d}",
            "user_name":         rand_name(),
            "registration_date": reg_dt,
            "user_segment":      segment,
        })
    filepath = os.path.join(CSV_DIR, "users.csv")
    write_csv(filepath, ["user_id","user_name","registration_date","user_segment"], rows)
    return [r["user_id"] for r in rows]

# ----------------------------------------────────────────────────────────────────────
# 3. GENERATE locations.csv  (MySQL.locations)
# ----------------------------------------────────────────────────────────────────────

def generate_locations():
    rows = []
    loc_id = 1
    for city, names in LOCATION_NAMES_BY_CITY.items():
        province = CITY_PROVINCE[city][0]
        for name in names:
            lat, lon = rand_lat_lon(city)
            zone = random.choice(ZONE_TYPES) if random.random() > 0.05 else None
            rows.append({
                "location_id":   f"LOC-{loc_id:04d}",
                "location_name": name,
                "city":          city,
                "province":      province,
                "latitude":      lat,
                "longitude":     lon,
                "zone_type":     zone,
            })
            loc_id += 1
    filepath = os.path.join(CSV_DIR, "locations.csv")
    write_csv(filepath, ["location_id","location_name","city","province",
                         "latitude","longitude","zone_type"], rows)
    return [r["location_id"] for r in rows]

# ----------------------------------------────────────────────────────────────────────
# 4. GENERATE trips_raw.csv  (PostgreSQL.trips_raw)
#    + payments.csv           (PostgreSQL.payments)
# ----------------------------------------────────────────────────────────────────────

def generate_trips_and_payments(driver_ids, user_ids, location_ids, n=5000):
    trip_rows    = []
    payment_rows = []
    payment_id   = 1

    # Buat pool trip_id unik (jumlah trip bersih)
    unique_trip_ids = [f"TRP-{i:06d}" for i in range(1, n + 1)]

    for i, trip_id in enumerate(unique_trip_ids):
        driver_id  = random.choice(driver_ids)
        user_id    = random.choice(user_ids)
        pickup_loc = random.choice(location_ids)
        # dropoff berbeda dari pickup
        dropoff_loc = random.choice([l for l in location_ids if l != pickup_loc])

        pickup_dt   = rand_datetime("2024-01-01", "2024-12-31")
        # Durasi normal 10-120 menit
        duration    = random.randint(10, 120)
        dropoff_dt  = pickup_dt + timedelta(minutes=duration)

        distance_km  = round(random.uniform(1.0, 40.0), 2)
        base_fare    = round(random.uniform(10000, 150000), 2)
        surge        = random.choices([1.0, 1.25, 1.5, 1.75, 2.0, 2.5],
                                      weights=[55, 15, 12, 8, 6, 4])[0]
        total_fare   = round(base_fare * surge, 2)
        trip_status  = random.choices(TRIP_STATUSES, weights=[80, 15, 5])[0]
        pay_method   = random.choice(PAYMENT_METHODS)
        pay_status   = random.choices(PAYMENT_STATUSES, weights=[85, 8, 7])[0]

        # ----------------------------------------─ DATA QUALITY ISSUES ──────────────────────────
        # DQ1: ~3% baris dengan distance_km = NULL
        if random.random() < 0.03:
            distance_km = None

        # DQ2: ~3% baris dengan base_fare = NULL
        if random.random() < 0.03:
            base_fare  = None
            total_fare = None

        # DQ3: ~2% baris dengan base_fare = 0
        if random.random() < 0.02:
            base_fare  = 0.0
            total_fare = 0.0

        # DQ4: ~2% baris dengan duration_minutes <= 0
        if random.random() < 0.02:
            duration = random.choice([-10, -5, 0])

        # DQ5: ~2% baris dengan surge_multiplier tidak valid
        if random.random() < 0.02:
            surge = random.choice([0.5, 0.8, 3.5, 5.0])

        # DQ6: ~3% baris dengan trip_status tidak konsisten (case berbeda)
        if random.random() < 0.03:
            trip_status = random.choice(
                ["completed","COMPLETED","Cancelled ","failed","CANCELLED"]
            )
        # ----------------------------------------────────────────────────────────────────────────

        base_row = {
            "trip_id":              trip_id,
            "driver_id":            driver_id,
            "user_id":              user_id,
            "pickup_location_id":   pickup_loc,
            "dropoff_location_id":  dropoff_loc,
            "pickup_time":          fmt_ts(pickup_dt),
            "dropoff_time":         fmt_ts(dropoff_dt),
            "distance_km":          distance_km,
            "duration_minutes":     duration,
            "base_fare":            base_fare,
            "surge_multiplier":     surge,
            "total_fare":           total_fare,
            "trip_status":          trip_status,
            "payment_method":       pay_method,
            "payment_status":       pay_status,
        }
        trip_rows.append(base_row)

        # DQ7: ~5% trip_id muncul 2x (duplicate) — raw_trip_id tetap unik (auto-increment)
        if random.random() < 0.05:
            dup = base_row.copy()
            trip_rows.append(dup)

        # payments: satu record per trip
        payment_rows.append({
            "payment_id":     payment_id,
            "trip_id":        trip_id,
            "payment_method": pay_method,
            "payment_status": pay_status,
        })
        payment_id += 1

    # Tulis trips_raw.csv — raw_trip_id (serial) di-generate saat INSERT ke DB
    # Tapi untuk CSV kita sertakan sebagai kolom agar mudah di-load
    final_trip_rows = []
    for idx, row in enumerate(trip_rows, start=1):
        r = {"raw_trip_id": idx}
        r.update(row)
        final_trip_rows.append(r)

    filepath_trips = os.path.join(CSV_DIR, "trips_raw.csv")
    write_csv(filepath_trips,
              ["raw_trip_id","trip_id","driver_id","user_id",
               "pickup_location_id","dropoff_location_id",
               "pickup_time","dropoff_time","distance_km","duration_minutes",
               "base_fare","surge_multiplier","total_fare",
               "trip_status","payment_method","payment_status"],
              final_trip_rows)

    filepath_pay = os.path.join(CSV_DIR, "payments.csv")
    write_csv(filepath_pay,
              ["payment_id","trip_id","payment_method","payment_status"],
              payment_rows)

    return unique_trip_ids

# ----------------------------------------────────────────────────────────────────────
# 5. GENERATE app_events.json  (MongoDB.app_events)
# ----------------------------------------────────────────────────────────────────────

def generate_app_events(trip_ids, user_ids):
    """
    Setiap trip ideal punya 6 event berurutan.
    Trip dengan status Cancelled/Failed mungkin hanya punya 1-3 event.
    Disisipkan berbagai data quality issues.
    """
    events     = []
    event_seq  = 1

    for trip_id in trip_ids:
        # Tentukan berapa event yang akan di-generate per trip (4-6)
        n_events = random.choices([6, 5, 4], weights=[85, 10, 5])[0]
        event_subset = EVENT_TYPES_ORDERED[:n_events]

        user_id    = random.choice(user_ids)
        device_os  = random.choice(DEVICE_OS_LIST)
        app_ver    = random.choice(APP_VERSIONS)

        # Waktu awal: ambil random
        base_time  = rand_datetime("2024-01-01", "2024-12-31")

        for order, etype in enumerate(event_subset):
            event_id = f"EVT-{event_seq:07d}"
            event_time = base_time + timedelta(minutes=order * random.randint(2, 10))

            # ----------------------------------------─ DATA QUALITY ISSUES ──────────────────────
            # DQ1: ~2% duplicate event_id (same event_id, different data)
            use_event_id = event_id
            if random.random() < 0.02 and event_seq > 1:
                use_event_id = f"EVT-{random.randint(1, event_seq - 1):07d}"

            # DQ2: ~3% event_time = NULL
            use_time = fmt_ts(event_time) if random.random() > 0.03 else None

            # DQ3: ~4% event_type format tidak konsisten
            use_etype = etype
            if random.random() < 0.04:
                variants = {
                    "booking_created": ["Booking Created","BOOKING_CREATED","booking-created"],
                    "driver_assigned": ["Driver Assigned","DRIVER_ASSIGNED","driver-assigned"],
                    "pickup_arrived":  ["Pickup Arrived","PICKUP_ARRIVED","pickup-arrived"],
                    "trip_started":    ["Trip Started","TRIP_STARTED","trip-started"],
                    "trip_completed":  ["Trip Completed","TRIP_COMPLETED","trip-completed"],
                    "payment_success": ["Payment Success","PAYMENT_SUCCESS","payment-success"],
                }
                use_etype = random.choice(variants.get(etype, [etype]))

            # DQ4: ~5% app_version = NULL atau ""
            use_app_ver = app_ver
            if random.random() < 0.05:
                use_app_ver = random.choice([None, ""])

            # DQ5: ~5% device_os = NULL atau ""
            use_device = device_os
            if random.random() < 0.05:
                use_device = random.choice([None, ""])
            # ----------------------------------------────────────────────────────────────────────

            events.append({
                "event_id":    use_event_id,
                "trip_id":     trip_id,
                "user_id":     user_id,
                "event_type":  use_etype,
                "event_time":  use_time,
                "device_os":   use_device,
                "app_version": use_app_ver,
            })
            event_seq += 1

    # Tulis ke JSON
    filepath = os.path.join(JSON_DIR, "app_events.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2, default=str)
    print(f"  [OK] {'app_events.json':30s}  ({len(events):,} documents)")
    return events

# ----------------------------------------────────────────────────────────────────────
# 6. GENERATE data_quality_report.md
# ----------------------------------------────────────────────────────────────────────

def generate_dq_report(trip_rows_count, events_count):
    content = f"""# Data Quality Report
**Proyek:** Data Warehouse & ETL Pipeline - Ride-Hailing Gojek  
**Orang   :** Anggota 2 — Data Generation  
**Tanggal :** {datetime.now().strftime('%Y-%m-%d')}  
**Versi   :** Final v1.0

---

## 1. Ringkasan Dataset

| File | Jumlah Record | Keterangan |
|------|--------------|------------|
| drivers.csv | 200 | Master data driver |
| users.csv | 500 | Master data pengguna |
| locations.csv | ~80 | Titik lokasi pickup & dropoff |
| trips_raw.csv | ~{trip_rows_count:,} | Transaksi trip (termasuk duplikat) |
| payments.csv | 5.000 | Referensi pembayaran per trip |
| app_events.json | ~{events_count:,} | Event log aplikasi |

---

## 2. Data Quality Issues — trips_raw.csv

| No | Kolom | Jenis Masalah | Persentase Estimasi | Penanganan Spark ETL |
|----|-------|--------------|--------------------|--------------------|
| 1 | distance_km | Missing value (NULL) | ~3% | Imputasi median |
| 2 | base_fare | Missing value (NULL) | ~3% | Imputasi median |
| 3 | base_fare | Nilai Rp0 | ~2% | Flag zero_fare |
| 4 | duration_minutes | Nilai ≤ 0 | ~2% | Drop baris |
| 5 | surge_multiplier | Nilai tidak valid (<1.0 atau >3.0) | ~2% | Drop / default 1.0 |
| 6 | trip_status | Format tidak konsisten | ~3% | Standardisasi title case |
| 7 | trip_id | Duplicate | ~5% | Ambil 1 baris per trip_id |

---

## 3. Data Quality Issues — app_events.json

| No | Field | Jenis Masalah | Persentase Estimasi | Penanganan Spark ETL |
|----|-------|--------------|--------------------|--------------------|
| 1 | event_id | Duplicate | ~2% | Drop duplicate |
| 2 | event_time | NULL / kosong | ~3% | Drop baris |
| 3 | event_type | Format tidak konsisten | ~4% | Standardisasi lowercase + underscore |
| 4 | app_version | NULL / kosong | ~5% | Isi 'Unknown' |
| 5 | device_os | NULL / kosong | ~5% | Isi 'Unknown' |

---

## 4. Catatan Penting

- `trip_id` pada `app_events.json` **100% berasal dari** `trips_raw.csv` agar join di Spark berhasil.
- `raw_trip_id` pada `trips_raw.csv` adalah surrogate PK teknis (auto-increment) — bukan business key.
- `trip_id` **sengaja tidak unik** di `trips_raw.csv` untuk mensimulasikan data quality issue duplikat.
- Semua data bersifat **synthetic** (tidak mengandung data pribadi nyata).
- Data menggunakan periode **1 Jan 2024 – 31 Des 2024**.

---

## 5. Cara Load Data ke Docker Container

### MySQL (drivers, users, locations)
```bash
docker exec -i mysql-source mysql -uroot -proot gojek_source_mysql < sql/mysql_source_schema.sql
docker exec -i mysql-source mysql -uroot -proot gojek_source_mysql -e "
LOAD DATA LOCAL INFILE '/data/source_csv/drivers.csv'
INTO TABLE drivers FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\\\"'
LINES TERMINATED BY '\\n' IGNORE 1 ROWS;"
```
Atau gunakan `load_mysql.py`.

### PostgreSQL Source (trips_raw, payments)
```bash
psql -h localhost -p 5434 -U postgres -d gojek_source_postgres -f sql/postgres_source_schema.sql
psql -h localhost -p 5434 -U postgres -d gojek_source_postgres -c "\\COPY trips_raw FROM 'data/source_csv/trips_raw.csv' CSV HEADER;"
psql -h localhost -p 5434 -U postgres -d gojek_source_postgres -c "\\COPY payments FROM 'data/source_csv/payments.csv' CSV HEADER;"
```
Atau gunakan `load_postgres.py`.

### MongoDB (app_events)
```bash
mongoimport --host localhost --port 27017 \\
  --db gojek_logs --collection app_events \\
  --file data/source_json/app_events.json --jsonArray
```
Atau gunakan `load_mongodb.py`.
"""
    os.makedirs("docs", exist_ok=True)
    with open("docs/data_quality_report.md", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {'data_quality_report.md':30s}")

# ----------------------------------------────────────────────────────────────────────
# MAIN
# ----------------------------------------────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Gojek DWH — Data Generation Script")
    print("  Anggota 2 — Final v1.0")
    print("=" * 60)

    print("\n[1/5] Generating drivers.csv ...")
    driver_ids, driver_city_map = generate_drivers(500)

    print("\n[2/5] Generating users.csv ...")
    user_ids = generate_users(2000)

    print("\n[3/5] Generating locations.csv ...")
    location_ids = generate_locations()

    print("\n[4/5] Generating trips_raw.csv & payments.csv ...")
    trip_ids = generate_trips_and_payments(driver_ids, user_ids, location_ids, n=6000)

    print("\n[5/5] Generating app_events.json ...")
    events = generate_app_events(trip_ids, user_ids)

    print("\n[+] Generating data_quality_report.md ...")
    trips_raw_count = int(6000 * 1.05)
    generate_dq_report(trips_raw_count, len(events))

    print("\n" + "=" * 60)
    print("  [DONE] Semua file berhasil di-generate!")
    print(f"  [DIR] CSV  -> {CSV_DIR}/")
    print(f"  [DIR] JSON -> {JSON_DIR}/")
    print(f"  [FILE] DQ Report -> docs/data_quality_report.md")
    print("=" * 60)
    print("\nFile output:")
    for f in os.listdir(CSV_DIR):
        fpath = os.path.join(CSV_DIR, f)
        size  = os.path.getsize(fpath)
        print(f"  {f:35s} {size/1024:8.1f} KB")
    for f in os.listdir(JSON_DIR):
        fpath = os.path.join(JSON_DIR, f)
        size  = os.path.getsize(fpath)
        print(f"  {f:35s} {size/1024:8.1f} KB")

if __name__ == "__main__":
    main()