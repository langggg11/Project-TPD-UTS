# -*- coding: utf-8 -*-
"""
load_mongodb.py
Kelompok 8 - Anggota 2: Data Generator & Source Preparation

Fungsi: Load app_events.json ke MongoDB
Collection : app_events
Database   : gojek_logs

CARA PAKAI:
1. Pastikan MongoDB berjalan di localhost:27017
2. Install pymongo: pip install pymongo
3. Jalankan: python load_mongodb.py
"""

import json
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from pymongo import MongoClient, ASCENDING
    from pymongo.errors import BulkWriteError
except ImportError:
    print("[ERROR] pymongo tidak terinstall.")
    print("        Jalankan: pip install pymongo")
    sys.exit(1)

# ── CONFIG ────────────────────────────────────────────────────
MONGO_HOST       = "localhost"
MONGO_PORT       = 27017
MONGO_DATABASE   = "gojek_logs"
MONGO_COLLECTION = "app_events"
DATA_DIR         = "data/source"
# ─────────────────────────────────────────────────────────────

print("=" * 55)
print("  LOAD DATA KE MONGODB - Kelompok 8")
print("=" * 55)

# Koneksi
try:
    client = MongoClient(MONGO_HOST, MONGO_PORT, serverSelectionTimeoutMS=5000)
    client.server_info()
    print(f"\n  [OK] Koneksi ke MongoDB berhasil")
    print(f"       {MONGO_HOST}:{MONGO_PORT}")
except Exception as e:
    print(f"\n  [ERROR] Gagal konek ke MongoDB: {e}")
    print(f"  Pastikan MongoDB berjalan: mongod --dbpath /data/db")
    sys.exit(1)

db         = client[MONGO_DATABASE]
collection = db[MONGO_COLLECTION]

# Baca JSON
json_path = f"{DATA_DIR}/app_events.json"
if not os.path.exists(json_path):
    print(f"\n  [ERROR] File tidak ditemukan: {json_path}")
    print(f"  Jalankan generate_data.py terlebih dahulu!")
    sys.exit(1)

with open(json_path, "r", encoding="utf-8") as f:
    events = json.load(f)

print(f"\n  [OK] Membaca {len(events):,} events dari {json_path}")

# Drop collection lama, insert ulang
collection.drop()
print(f"  [OK] Collection lama dihapus, insert ulang...")

# Insert dalam batch
BATCH_SIZE = 1000
total_inserted = 0
for i in range(0, len(events), BATCH_SIZE):
    batch = events[i:i+BATCH_SIZE]
    try:
        result = collection.insert_many(batch, ordered=False)
        total_inserted += len(result.inserted_ids)
    except BulkWriteError as bwe:
        total_inserted += bwe.details.get("nInserted", 0)

# Buat index
collection.create_index([("trip_id",   ASCENDING)])
collection.create_index([("event_type",ASCENDING)])
collection.create_index([("user_id",   ASCENDING)])
print(f"  [OK] Index dibuat pada: trip_id, event_type, user_id")

print(f"\n  [OK] Total inserted: {total_inserted:,} documents")
print(f"       Database   : {MONGO_DATABASE}")
print(f"       Collection : {MONGO_COLLECTION}")

# Verifikasi
count = collection.count_documents({})
sample = collection.find_one()
print(f"\n  Verifikasi:")
print(f"    Total dokumen  : {count:,}")
print(f"    Contoh dokumen : {json.dumps(sample, default=str, ensure_ascii=False)[:200]}")

# Distribusi event_type
print(f"\n  Distribusi event_type:")
pipeline = [{"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}]
for doc in collection.aggregate(pipeline):
    print(f"    {doc['_id']:<30} : {doc['count']:,}")

print(f"\n  [DONE] Load ke MongoDB selesai!")
print(f"  Cek di MongoDB Compass: {MONGO_DATABASE} > {MONGO_COLLECTION}")
print("=" * 55)

client.close()
