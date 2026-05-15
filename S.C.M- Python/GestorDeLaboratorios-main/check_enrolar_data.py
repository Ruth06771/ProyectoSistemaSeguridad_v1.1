#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from config.db import get_connection

conn = get_connection()
cur = conn.cursor()

# Get table info
print("=== Estructura de tabla enrolar ===")
cur.execute("PRAGMA table_info(enrolar)")
columns = cur.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check enrolar table
print("\n=== Verificando tabla enrolar ===")
cur.execute("SELECT COUNT(*) FROM enrolar")
count = cur.fetchone()[0]
print(f"Total de registros en enrolar: {count}")

if count > 0:
    cur.execute("""
        SELECT 
            e.id,
            p.nombre_completo,
            t.uid,
            e.fecha_registro,
            e.estado,
            e.accion
        FROM enrolar e
        LEFT JOIN personas p ON p.id = e.persona_id
        LEFT JOIN tarjetas t ON t.id = e.tarjeta_id OR (e.tarjeta_uid IS NOT NULL AND t.uid = e.tarjeta_uid)
        ORDER BY e.id DESC
    """)
    rows = cur.fetchall()
    print("\nDatos de enrolar:")
    for row in rows:
        print(f"  ID: {row[0]}, Persona: {row[1]}, Tarjeta: {row[2]}, Fecha: {row[3]}, Estado: {row[4]}, Acción: {row[5]}")

cur.close()
conn.close()


