#!/usr/bin/env python3
"""
Test script to verify the /api/enrolar endpoint works after fix.
Simulates what the frontend would get.
"""
import sys
sys.path.insert(0, '.')

from config.db import get_connection

def _row_to_dict(cursor, row):
    """Convert SQLite row to dict using cursor.description"""
    if hasattr(row, 'keys'):
        return dict(row)
    cols = [desc[0] for desc in cursor.description]
    return dict(zip(cols, row))

conn = get_connection()
cursor = conn.cursor()

# Execute the same query as the endpoint
sql = '''
SELECT
    e.id AS enrolar_id,
    e.persona_id,
    e.tarjeta_id,
    e.tarjeta_uid,
    e.perfil_acceso_lab_id,
    e.estado AS enrolar_estado,
    e.accion AS enrolar_accion,
    e.fecha_registro,
    p.nombre_completo AS persona_nombre,
    p.correo AS persona_correo,
    p.documento_identidad AS persona_documento,
    p.tipo_sangre AS persona_tipo_sangre,
    p.estado AS persona_estado,
    t.uid AS tarjeta_uid_real,
    t.pin AS tarjeta_pin,
    t.estado AS tarjeta_estado,
    pa.nombre AS perfil_nombre
FROM enrolar e
LEFT JOIN personas p ON p.id = e.persona_id
LEFT JOIN tarjetas t ON t.id = e.tarjeta_id OR (e.tarjeta_uid IS NOT NULL AND t.uid = e.tarjeta_uid)
LEFT JOIN perfil_acceso_lab pa ON pa.id = e.perfil_acceso_lab_id
ORDER BY e.fecha_registro DESC
'''

cursor.execute(sql)
rows = cursor.fetchall()
results = []
for r in rows:
    row = _row_to_dict(cursor, r)
    results.append({
        'id': row.get('enrolar_id'),
        'persona_id': row.get('persona_id'),
        'tarjeta_id': row.get('tarjeta_id'),
        'tarjeta_uid': row.get('tarjeta_uid_real') or row.get('tarjeta_uid'),
        'perfil_id': row.get('perfil_acceso_lab_id'),
        'perfil': row.get('perfil_nombre'),
        'accion': row.get('enrolar_accion'),
        'estado': row.get('enrolar_estado'),
        'fecha_de_registro': row.get('fecha_registro'),
        'nombre_completo': row.get('persona_nombre'),
        'correo': row.get('persona_correo'),
        'documento_identidad': row.get('persona_documento'),
        'tipo_sangre': row.get('persona_tipo_sangre'),
        'persona_estado': row.get('persona_estado'),
        'pin': row.get('tarjeta_pin'),
        'tarjeta_estado': row.get('tarjeta_estado')
    })

cursor.close()
conn.close()

print(f"✅ Query executed successfully - {len(results)} records found\n")
print("Sample response (as JSON):")
import json
print(json.dumps(results[:2], indent=2, ensure_ascii=False))
print(f"\n... and {len(results)-2} more records")
