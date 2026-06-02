#!/usr/bin/env python
"""Script para testear el endpoint POST /api/enrolar"""
import sys
import json
sys.path.insert(0, '/S.C.M- Python/GestorDeLaboratorios-main')

from config.db import get_connection

connection = get_connection()
cursor = connection.cursor()

print("=" * 60)
print("PRUEBA: Verificar estructura de datos")
print("=" * 60)

# Obtener una persona existente
cursor.execute("SELECT id, nombre_completo FROM personas LIMIT 1")
persona = cursor.fetchone()
if persona:
    print(f"✓ Persona de prueba: ID={persona[0]}, Nombre={persona[1]}")
else:
    print("✗ No hay personas en la base de datos")
    sys.exit(1)

# Obtener una tarjeta existente
cursor.execute("SELECT id, uid FROM tarjetas LIMIT 1")
tarjeta = cursor.fetchone()
if tarjeta:
    print(f"✓ Tarjeta de prueba: ID={tarjeta[0]}, UID={tarjeta[1]}")
else:
    print("✗ No hay tarjetas en la base de datos")
    sys.exit(1)

# Obtener perfil
cursor.execute("SELECT id, nombre FROM perfil_acceso_lab LIMIT 1")
perfil = cursor.fetchone()
if perfil:
    print(f"✓ Perfil de prueba: ID={perfil[0]}, Nombre={perfil[1]}")
else:
    print("✗ No hay perfiles en la base de datos")
    sys.exit(1)

print("\n" + "=" * 60)
print("SIMULACIÓN: Payload que debería enviar el frontend")
print("=" * 60)

payload = {
    "persona": {
        "nombre_completo": persona[1],
        "correo": "test@example.com",
        "tipo_sangre": "O+",
        "documento_identidad": "123456789"
    },
    "tarjeta": {
        "uid": tarjeta[1],
        "nombre_completo": persona[1],
        "correo": "test@example.com",
        "pin": "1234"
    },
    "perfil": {
        "perfil_acceso_lab_id": perfil[0],
        "nombre": perfil[1]
    }
}

print(json.dumps(payload, indent=2, ensure_ascii=False))

print("\n" + "=" * 60)
print("INSTRUCCIONES")
print("=" * 60)
print("1. Abre la consola del navegador (F12)")
print("2. Ve a Enrolar, llena los campos y haz clic en 'Enrolar ahora'")
print("3. Revisa en la consola si ves:")
print("   - '[handleSubmit] Response status: 200'")
print("   - '[handleSubmit] Response data: {success: true, ...}'")
print("4. Si ves un error, cópialo y comparte")

connection.close()
print("\n✓ Script de test completado")
