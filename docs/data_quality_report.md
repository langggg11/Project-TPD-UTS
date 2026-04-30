# Data Quality Report
**Proyek:** Data Warehouse & ETL Pipeline - Ride-Hailing Gojek  
**Orang   :** Anggota 2 — Data Generation  
**Tanggal :** 2026-04-30  
**Versi   :** Final v1.0

---

## 1. Ringkasan Dataset

| File | Jumlah Record | Keterangan |
|------|--------------|------------|
| drivers.csv | 200 | Master data driver |
| users.csv | 500 | Master data pengguna |
| locations.csv | ~80 | Titik lokasi pickup & dropoff |
| trips_raw.csv | ~6,300 | Transaksi trip (termasuk duplikat) |
| payments.csv | 5.000 | Referensi pembayaran per trip |
| app_events.json | ~34,800 | Event log aplikasi |

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
INTO TABLE drivers FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"'
LINES TERMINATED BY '\n' IGNORE 1 ROWS;"
```
Atau gunakan `load_mysql.py`.

### PostgreSQL Source (trips_raw, payments)
```bash
psql -h localhost -p 5434 -U postgres -d gojek_source_postgres -f sql/postgres_source_schema.sql
psql -h localhost -p 5434 -U postgres -d gojek_source_postgres -c "\COPY trips_raw FROM 'data/source_csv/trips_raw.csv' CSV HEADER;"
psql -h localhost -p 5434 -U postgres -d gojek_source_postgres -c "\COPY payments FROM 'data/source_csv/payments.csv' CSV HEADER;"
```
Atau gunakan `load_postgres.py`.

### MongoDB (app_events)
```bash
mongoimport --host localhost --port 27017 \
  --db gojek_logs --collection app_events \
  --file data/source_json/app_events.json --jsonArray
```
Atau gunakan `load_mongodb.py`.
