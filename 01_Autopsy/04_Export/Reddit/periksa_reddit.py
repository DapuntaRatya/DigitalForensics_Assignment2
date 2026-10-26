from pathlib import Path
from datetime import datetime, timedelta, timezone
import hashlib
import plistlib

path = Path(__file__).resolve().parent / "78918-ivu21eum"
raw = path.read_bytes()
before = hashlib.sha256(raw).hexdigest()
archive = plistlib.loads(raw)

# Ikuti referensi UID dalam arsip NSKeyedArchiver.
objects = archive["$objects"]
account = objects[archive["$top"]["root"].data]
redditor = objects[account["kRedditorKey"].data]
username = objects[redditor["Username"].data]
created = objects[account["created"].data]
seconds = created["NS.time"]

epoch = datetime(2001, 1, 1, tzinfo=timezone.utc)
created_utc = epoch + timedelta(seconds=seconds)

print(f"File: {path.name}")
print(f"SHA-256: {before}")
print(f"Archiver: {archive['$archiver']}")
print(f"Username: {username}")
print(f"created > NS.time: {seconds}")
print(f"Tanggal pembuatan UTC: {created_utc.isoformat()}")
print(f"Jawaban waktu UTC: {created_utc:%H:%M:%S}")

after = hashlib.sha256(path.read_bytes()).hexdigest()
if after != before:
    raise RuntimeError("Hash file berubah.")
print("Verifikasi: hash file ekspor tetap sama.")