from pathlib import Path
import hashlib
import plistlib

path = Path(__file__).resolve().parent / "com.apple.mobiletimerd.plist"
raw = path.read_bytes()
before = hashlib.sha256(raw).hexdigest()
data = plistlib.loads(raw)
alarms = data["MTAlarms"]["MTAlarms"]

print(f"File: {path.name}")
print(f"SHA-256: {before}")
print(f"Jumlah alarm: {len(alarms)}")

for index, item in enumerate(alarms, start=1):
    alarm = item["$MTAlarm"]
    sound = alarm["MTAlarmSound"]["$MTSound"]
    print(f"\nAlarm {index}")
    print(f"Judul: {alarm['MTAlarmTitle']}")
    print(f"Waktu: {alarm['MTAlarmHour']:02d}:{alarm['MTAlarmMinute']:02d}")
    print(f"Aktif: {alarm['MTAlarmEnabled']}")
    print(f"MTSoundToneID: {sound['MTSoundToneID']}")

if hashlib.sha256(path.read_bytes()).hexdigest() != before:
    raise RuntimeError("Hash file berubah.")
print("\nVerifikasi: hash file ekspor tetap sama.")