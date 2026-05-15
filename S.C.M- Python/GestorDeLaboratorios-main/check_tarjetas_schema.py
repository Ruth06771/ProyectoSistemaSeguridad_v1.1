#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from config.db import get_connection

conn = get_connection()
cur = conn.cursor()

# List all tables
print("=== Tablas en la base de datos ===")
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cur.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# Check tarjetas table structure
print("\n=== Estructura tabla 'tarjetas' ===")
try:
    cur.execute("PRAGMA table_info(tarjetas)")
    columns = cur.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
except:
    print("  Tabla tarjetas no encontrada")

# Check historial_tarjetas table structure
print("\n=== Estructura tabla 'historial_tarjetas' (si existe) ===")
try:
    cur.execute("PRAGMA table_info(historial_tarjetas)")
    columns = cur.fetchall()
    if columns:
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    else:
        print("  Tabla no existe")
except:
    print("  Tabla no existe")

# Count records
print("\n=== Datos actuales ===")
cur.execute("SELECT COUNT(*) FROM tarjetas")
print(f"Total tarjetas: {cur.fetchone()[0]}")

try:
    cur.execute("SELECT COUNT(*) FROM historial_tarjetas")
    print(f"Total historial_tarjetas: {cur.fetchone()[0]}")
except:
    print("historial_tarjetas: tabla no existe")

cur.close()
conn.close()
