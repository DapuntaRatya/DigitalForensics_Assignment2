from pathlib import Path
import gzip
import hashlib
import re
import shutil
import sqlite3
import tempfile

folder = Path(__file__).resolve().parent
files = {
    "78909-NoteStore.sqlite": "NoteStore.sqlite",
    "78910-NoteStore.sqlite-shm": "NoteStore.sqlite-shm",
    "78911-NoteStore.sqlite-wal": "NoteStore.sqlite-wal",
}

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

hashes = {}
print("SHA-256 file hasil ekspor:")
for original in files:
    path = folder / original
    hashes[original] = sha256(path)
    print(f"{original}: {hashes[original]}")

with tempfile.TemporaryDirectory() as temporary:
    work = Path(temporary)
    for original, target in files.items():
        shutil.copyfile(folder / original, work / target)

    uri = (work / "NoteStore.sqlite").as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    try:
        print("\nIntegritas SQLite:",
              connection.execute("PRAGMA integrity_check").fetchone()[0])
        row = connection.execute("""
            SELECT o.Z_PK, d.Z_PK, o.ZTITLE1, d.ZDATA
            FROM ZICCLOUDSYNCINGOBJECT AS o
            JOIN ZICNOTEDATA AS d ON o.ZNOTEDATA = d.Z_PK
            WHERE o.ZTITLE1 = ?
        """, ("Grocery list",)).fetchone()

        if row is None:
            raise ValueError("Catatan Grocery list tidak ditemukan.")

        note_id, data_id, title, blob = row
        decompressed = gzip.decompress(blob)

        # Ambil rangkaian teks mulai dari judul hingga kontrol biner.
        # Pola ini khusus untuk catatan yang sedang diperiksa.
        pattern = re.escape(title.encode("utf-8"))
        pattern += rb"[^\x00-\x08\x0b-\x1f\x7f]*"
        match = re.search(pattern, decompressed)
        if match is None:
            raise ValueError("Teks catatan tidak ditemukan.")

        lines = [
            line.strip()
            for line in match.group().decode("utf-8").splitlines()
            if line.strip()
        ]
        print(f"ID catatan: {note_id}; ID data: {data_id}")
        print("\nIsi catatan:")
        print("\n".join(lines))
        print(f"\nJumlah item di luar judul: {len(lines) - 1}")
    finally:
        connection.close()

for original, expected in hashes.items():
    if sha256(folder / original) != expected:
        raise RuntimeError(f"Hash berubah: {original}")
print("\nVerifikasi: hash ketiga file ekspor tetap sama.")