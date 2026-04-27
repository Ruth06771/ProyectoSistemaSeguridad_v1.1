import sqlite3
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB = os.path.join(ROOT, 'data', 'dev.sqlite3')
os.makedirs(os.path.dirname(DB), exist_ok=True)

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS Dispositivos (
    IdDispositivo INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT NOT NULL,
    ApiKey TEXT NOT NULL UNIQUE,
    Activo INTEGER NOT NULL DEFAULT 1,
    FechaRegistro DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
cur.execute('INSERT OR IGNORE INTO Dispositivos (Nombre,ApiKey,Activo) VALUES (?,?,1)', ('ESP32-Test','MI_PRUEBA_CLAVE'))
conn.commit()
cur.execute('SELECT IdDispositivo,Nombre,ApiKey,Activo FROM Dispositivos')
print(cur.fetchall())
conn.close()
