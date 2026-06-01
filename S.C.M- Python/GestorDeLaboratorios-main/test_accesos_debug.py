#!/usr/bin/env python3
"""
Script para debuggear el historial de accesos.
Verifica:
1. Datos en la BD (historial_tarjetas y registro_acceso)
2. Si la API devuelve datos correctamente
3. Problemas de sincronización
"""

import sqlite3
import json
from pathlib import Path

# Ubicar la BD
DB_PATH = Path(__file__).resolve().parent / 'data' / 'dev.sqlite3'

if not DB_PATH.exists():
    print(f"❌ Base de datos no encontrada en: {DB_PATH}")
    exit(1)

print(f"📁 Base de datos: {DB_PATH}")
print("=" * 80)

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Revisar si existen las tablas
print("\n1️⃣ VERIFICAR TABLAS")
print("-" * 80)
try:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('historial_tarjetas', 'registro_acceso', 'tarjetas', 'enrolar', 'personas')")
    tables = cur.fetchall()
    for t in tables:
        print(f"✅ Tabla existe: {t['name']}")
    if not tables:
        print("❌ No hay tablas de acceso/historial")
except Exception as e:
    print(f"❌ Error: {e}")

# 2. Contar registros en historial_tarjetas
print("\n2️⃣ REGISTROS EN HISTORIAL_TARJETAS")
print("-" * 80)
try:
    cur.execute("SELECT COUNT(*) as total FROM historial_tarjetas")
    result = cur.fetchone()
    total = result['total'] if result else 0
    print(f"Total registros: {total}")
    
    if total > 0:
        print("\nÚltimos 5 registros:")
        cur.execute("""
            SELECT id, tarjeta_id, uid, accion, ejecutado_por, fecha_hora, descripcion 
            FROM historial_tarjetas 
            ORDER BY fecha_hora DESC 
            LIMIT 5
        """)
        for row in cur.fetchall():
            print(f"  ID: {row['id']} | UID: {row['uid']} | Acción: {row['accion']} | Hora: {row['fecha_hora']}")
    else:
        print("⚠️  NO HAY REGISTROS EN historial_tarjetas")
except Exception as e:
    print(f"❌ Error: {e}")

# 3. Contar registros en registro_acceso
print("\n3️⃣ REGISTROS EN REGISTRO_ACCESO")
print("-" * 80)
try:
    cur.execute("SELECT COUNT(*) as total FROM registro_acceso")
    result = cur.fetchone()
    total = result['total'] if result else 0
    print(f"Total registros: {total}")
    
    if total > 0:
        print("\nÚltimos 5 registros:")
        cur.execute("""
            SELECT id, enrolar_id, tarjeta_uid, fecha_hora, resultado, credencial 
            FROM registro_acceso 
            ORDER BY fecha_hora DESC 
            LIMIT 5
        """)
        for row in cur.fetchall():
            print(f"  ID: {row['id']} | UID: {row['tarjeta_uid']} | Resultado: {row['resultado']} | Hora: {row['fecha_hora']}")
    else:
        print("⚠️  NO HAY REGISTROS EN registro_acceso")
except Exception as e:
    print(f"❌ Error: {e}")

# 4. Verificar tarjetas
print("\n4️⃣ TARJETAS REGISTRADAS")
print("-" * 80)
try:
    cur.execute("SELECT COUNT(*) as total FROM tarjetas")
    result = cur.fetchone()
    total = result['total'] if result else 0
    print(f"Total tarjetas: {total}")
    
    if total > 0:
        print("\nÚltimas 5 tarjetas:")
        cur.execute("SELECT id, uid, fecha_registro FROM tarjetas ORDER BY id DESC LIMIT 5")
        for row in cur.fetchall():
            print(f"  ID: {row['id']} | UID: {row['uid']}")
except Exception as e:
    print(f"❌ Error: {e}")

# 5. Verificar enrolar para UID específico
UID_CHECK = 'E3314E1C'
print("\n5️⃣ VERIFICAR ENROLAR para UID E3314E1C")
print("-" * 80)
try:
    cur.execute('SELECT id, persona_id, tarjeta_uid, tarjeta_id, estado FROM enrolar WHERE tarjeta_uid = ?', (UID_CHECK,))
    rows = cur.fetchall()
    print('Enrolar por tarjeta_uid:', [dict(r) for r in rows])
    cur.execute('SELECT id, persona_id, tarjeta_uid, tarjeta_id, estado FROM enrolar WHERE tarjeta_id IN (SELECT id FROM tarjetas WHERE uid = ?)', (UID_CHECK,))
    rows = cur.fetchall()
    print('Enrolar por tarjeta_id:', [dict(r) for r in rows])
    cur.execute('SELECT COUNT(*) as total FROM enrolar WHERE tarjeta_uid = ? OR tarjeta_id IN (SELECT id FROM tarjetas WHERE uid = ?)', (UID_CHECK, UID_CHECK))
    print('Total matching enrolar rows:', cur.fetchone()['total'])
except Exception as e:
    print(f"❌ Error: {e}")

# 6. Simular la query de la API
print("\n6️⃣ SIMULANDO QUERY DE LA API (accesos_historial)")
print("-" * 80)
try:
    sql = """
    SELECT 
        ht.id,
        ht.fecha_hora,
        COALESCE(p.nombre_completo, ht.nombre_completo, 'Desconocido') AS persona,
        'Acceso' AS movimiento,
        ht.uid AS tarjeta_uid,
        ht.descripcion
    FROM historial_tarjetas ht
    LEFT JOIN tarjetas t ON ht.tarjeta_id = t.id
    LEFT JOIN enrolar e ON t.uid = e.tarjeta_uid
    LEFT JOIN personas p ON e.persona_id = p.id
    ORDER BY ht.fecha_hora DESC
    LIMIT 10
    """
    
    cur.execute(sql)
    rows = cur.fetchall()
    print(f"Registros retornados: {len(rows)}")
    
    if len(rows) > 0:
        print("\n✅ La API devolvería estos datos:")
        for row in rows:
            data = dict(row)
            print(f"  {json.dumps(data, indent=2, default=str)}")
    else:
        print("❌ La API retornaría lista vacía")
        
except Exception as e:
    print(f"❌ Error en query de API: {e}")

# 6. Verificar si hay dispositivos con API key
print("\n6️⃣ DISPOSITIVOS CONFIGURADOS")
print("-" * 80)
try:
    cur.execute("SELECT id, nombre, api_key, activo FROM dispositivos LIMIT 5")
    rows = cur.fetchall()
    if rows:
        print(f"Total dispositivos encontrados:")
        for row in rows:
            print(f"  ID: {row['id']} | Nombre: {row['nombre']} | API Key: {row['api_key'][:20]}... | Activo: {row['activo']}")
    else:
        print("⚠️  NO HAY DISPOSITIVOS CONFIGURADOS")
except Exception as e:
    print(f"⚠️  Error: {e}")

conn.close()

print("\n" + "=" * 80)
print("📝 RESUMEN DEL DEBUG:")
print("=" * 80)
print("""
Si ves:
✅ Registros en historial_tarjetas pero NO en registro_acceso
  → Los usuarios probablemente NO están enrolados (sin persona vinculada)
  
✅ Registros en la query simulada de la API
  → El backend debería devolverlos correctamente
  → Verifica la consola del navegador (F12) para errores
  
❌ NO hay registros en historial_tarjetas
  → El ESP32 NO está enviando datos o hay error en esp_api.py
  → Verifica que ESP32 tenga API Key correcta: MI_PRUEBA_CLAVE
  
❌ La query de la API devuelve vacío
  → Hay un problema con el JOIN a tarjetas/enrolar/personas
  → Los UIDs no coinciden entre tablas
""")
