#!/usr/bin/env python
"""Debug script para verificar perfiles en la base de datos"""
import sys
sys.path.insert(0, '/S.C.M- Python/GestorDeLaboratorios-main')

from config.db import get_connection

connection = get_connection()
cursor = connection.cursor()

print("=" * 60)
print("TABLA: perfil_acceso_lab")
print("=" * 60)
cursor.execute("SELECT id, nombre, estado FROM perfil_acceso_lab ORDER BY id ASC")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Nombre: {row[1]}, Estado: {row[2]}")

print("\n" + "=" * 60)
print("TABLA: enrolar (últimos 5)")
print("=" * 60)
cursor.execute("""
    SELECT 
        e.id, e.persona_id, e.perfil_acceso_lab_id, e.accion,
        p.nombre_completo,
        pa.nombre as perfil_nombre
    FROM enrolar e
    LEFT JOIN personas p ON p.id = e.persona_id
    LEFT JOIN perfil_acceso_lab pa ON pa.id = e.perfil_acceso_lab_id
    ORDER BY e.id DESC LIMIT 5
""")
for row in cursor.fetchall():
    print(f"Enrolar ID: {row[0]}, Persona: {row[4]}, Perfil ID: {row[2]}, Perfil Nombre: {row[5]}, Acción: {row[3]}")

connection.close()
print("\n✓ Debug completado")
