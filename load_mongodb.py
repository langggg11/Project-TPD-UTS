"""
load_mongodb.py
Load app_events.json ke MongoDB container.
Jalankan setelah generate_data.py.

Kebutuhan:
  pip install pymongo
"""

import json
import os

try:
    from pymongo import MongoClient, ASCENDING
    from pymongo.errors import BulkWriteError
except ImportError:
    raise ImportError("Jalankan: pip install pymongo")

# ── Konfigurasi koneksi ──────────────────────
MONGO_URI  = "mongodb://localhost:27017"
DB_NAME    = "gojek_logs"
COLLECTION = "app_events"

JSON_DIR = os.path.join("data", "source_json")


def main():
    print("=" * 50)
    print("  Load MongoDB — Gojek DWH")
    print("=" * 50)

    filepath = os.path.join(JSON_DIR, "app_events.json")
    with open(filepath, "r", encoding="utf-8") as f:
        events = json.load(f)

    print(f"  Loaded {len(events):,} documents dari {filepath}")

    client = MongoClient(MONGO_URI)
    db     = client[DB_NAME]
    col    = db[COLLECTION]

    # Drop collection lama agar bisa di-reload
    col.drop()
    print(f"  Existing collection '{COLLECTION}' dropped.")

    # Insert dalam batch
    BATCH = 1000
    inserted = 0
    for i in range(0, len(events), BATCH):
        batch = events[i: i + BATCH]
        try:
            result = col.insert_many(batch, ordered=False)
            inserted += len(result.inserted_ids)
        except BulkWriteError as bwe:
            # Beberapa dokumen mungkin gagal karena _id duplikat (jika ada)
            inserted += bwe.details.get("nInserted", 0)
            print(f"  ⚠  BulkWriteError di batch {i//BATCH}: {bwe.details['nInserted']} inserted")

    # Buat index untuk performa query
    col.create_index([("trip_id",    ASCENDING)])
    col.create_index([("event_id",   ASCENDING)])
    col.create_index([("event_type", ASCENDING)])
    print(f"  Index dibuat: trip_id, event_id, event_type")

    # Verifikasi
    count = col.count_documents({})
    print(f"\n  ✅  MongoDB load selesai!")
    print(f"  Total dokumen di collection '{COLLECTION}': {count:,}")

    # Sample dokumen
    sample = col.find_one({}, {"_id": 0})
    print(f"\n  Sample dokumen:\n  {json.dumps(sample, indent=4, default=str)}")

    client.close()


if __name__ == "__main__":
    main()
