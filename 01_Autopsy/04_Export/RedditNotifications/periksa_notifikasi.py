from pathlib import Path
from datetime import datetime, timedelta, timezone
import hashlib
import plistlib

folder = Path(__file__).resolve().parent
path = folder / "DeliveredNotifications.plist"
raw = path.read_bytes()
before = hashlib.sha256(raw).hexdigest()
archive = plistlib.loads(raw)
objects = archive["$objects"]

def resolve(value):
    return objects[value.data] if isinstance(value, plistlib.UID) else value

root = resolve(archive["$top"]["root"])
records = []
for reference in root["NS.objects"]:
    item = resolve(reference)
    record = {
        resolve(key): resolve(value)
        for key, value in zip(item["NS.keys"], item["NS.objects"])
    }
    records.append(record)

latest = max(
    records,
    key=lambda item: item["AppNotificationCreationDate"]["NS.time"]
)
seconds = latest["AppNotificationCreationDate"]["NS.time"]
epoch = datetime(2001, 1, 1, tzinfo=timezone.utc)
created_utc = epoch + timedelta(seconds=seconds)

print(f"File: {path.name}")
print(f"SHA-256: {before}")
print(f"Jumlah rekaman: {len(records)}")
print("Pemilihan: AppNotificationCreationDate terbesar")
print(f"NS.time: {seconds}")
print(f"Waktu UTC: {created_utc.isoformat()}")
print(f"Judul: {latest['AppNotificationTitle']}")
print(f"Isi: {latest['AppNotificationMessage']}")

if hashlib.sha256(path.read_bytes()).hexdigest() != before:
    raise RuntimeError("Hash file berubah.")
print("Verifikasi: hash file ekspor tetap sama.")