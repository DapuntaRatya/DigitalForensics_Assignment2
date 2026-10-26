from pathlib import Path
from datetime import datetime, timezone
import hashlib
import plistlib
import shutil
import sqlite3
import tempfile

folder = Path(__file__).resolve().parent
files = {
    "73029-Chat.sqlite": "Chat.sqlite",
    "73030-Chat.sqlite-shm": "Chat.sqlite-shm",
    "73031-Chat.sqlite-wal": "Chat.sqlite-wal",
}

def hashes():
    return {
        name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
        for name in files
    }

before = hashes()
print("SHA-256 file hasil ekspor:")
for name, digest in before.items():
    print(f"{name}: {digest}")

with tempfile.TemporaryDirectory() as temp:
    work = Path(temp)
    for source, target in files.items():
        shutil.copy2(folder / source, work / target)

    uri = (work / "Chat.sqlite").as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    try:
        print("\nIntegritas SQLite:",
              connection.execute("PRAGMA integrity_check").fetchone()[0])

        query = """
            SELECT d.rowid, d.key, d.data, i.isIncoming
            FROM database2 AS d
            JOIN secondaryIndex_isReadIndex AS i ON i.rowid = d.rowid
            ORDER BY d.rowid
        """
        found = 0
        for rowid, key, data, incoming in connection.execute(query):
            archive = plistlib.loads(data)
            objects = archive["$objects"]
            message = objects[archive["$top"]["root"].data]

            def value(field):
                item = message.get(field)
                return objects[item.data] if isinstance(item, plistlib.UID) else item

            text = value("self.messageText")
            if not isinstance(text, str) or "giphy.com/" not in text:
                continue

            found += 1
            timestamp = value("self.dateCreated")
            print("\nRow ID:", rowid)
            print("ID pesan:", key)
            print("isIncoming:", incoming)
            print("Waktu UTC:",
                  datetime.fromtimestamp(timestamp, timezone.utc).isoformat())
            print("Isi pesan:", text)

        print("\nJumlah pesan bertautan GIPHY:", found)
    finally:
        connection.close()

print("Hash file ekspor tetap sama:", before == hashes())