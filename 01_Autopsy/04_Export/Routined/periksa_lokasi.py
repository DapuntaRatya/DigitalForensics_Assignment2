from pathlib import Path
from datetime import datetime, timedelta, timezone
import hashlib
import shutil
import sqlite3
import tempfile

folder = Path(__file__).resolve().parent
names = ["Cache.sqlite", "Cache.sqlite-wal", "Cache.sqlite-shm"]

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

hashes = {name: sha256(folder / name) for name in names}
print("SHA-256 file hasil ekspor:")
for name, digest in hashes.items():
    print(f"{name}: {digest}")

with tempfile.TemporaryDirectory() as temporary:
    work = Path(temporary)
    for name in names:
        shutil.copyfile(folder / name, work / name)

    uri = (work / "Cache.sqlite").as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        count = connection.execute(
            "SELECT COUNT(*) FROM ZRTCLLOCATIONMO"
        ).fetchone()[0]
        row = connection.execute("""
            SELECT Z_PK, ZTIMESTAMP, ZLATITUDE,
                   ZLONGITUDE, ZHORIZONTALACCURACY
            FROM ZRTCLLOCATIONMO
            WHERE ZTIMESTAMP IS NOT NULL
            ORDER BY ZTIMESTAMP DESC, Z_PK DESC
            LIMIT 1
        """).fetchone()
        if row is None:
            raise ValueError("Tidak ditemukan rekaman lokasi.")

        record_id, timestamp, latitude, longitude, accuracy = row
        epoch = datetime(2001, 1, 1, tzinfo=timezone.utc)
        recorded_at = epoch + timedelta(seconds=timestamp)

        print(f"\nIntegritas SQLite: {integrity}")
        print(f"Jumlah entri dengan WAL: {count}")
        print(f"ID baris: {record_id}")
        print(f"Timestamp asli: {timestamp}")
        print(f"Waktu UTC: {recorded_at.isoformat()}")
        print(f"Latitude: {latitude:.8f}")
        print(f"Longitude: {longitude:.8f}")
        print(f"Akurasi horizontal: {accuracy} meter")
    finally:
        connection.close()

for name, expected in hashes.items():
    if sha256(folder / name) != expected:
        raise RuntimeError(f"Hash berubah: {name}")
print("\nVerifikasi: hash ketiga file ekspor tetap sama.")