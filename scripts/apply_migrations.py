import sqlite3
from pathlib import Path

DB_PATH = Path('instance/shornbee.db')
DB_PATH.parent.mkdir(exist_ok=True)
conn = sqlite3.connect(DB_PATH)
for sql_file in sorted(Path('migrations').glob('*.sql')):
    conn.executescript(sql_file.read_text())
    print(f"Applied {sql_file}")
conn.commit()
conn.close()
