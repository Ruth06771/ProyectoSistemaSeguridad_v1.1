#!/usr/bin/env python3
"""
Configurar permisos específicos para el rol Auxiliar:
- Administración: ver=1, crear=0, editar=0, eliminar=0
- Enrolar: ver=1, crear=0, editar=0, eliminar=0
- Reportes: ver=1, crear=0, editar=0, eliminar=0
- Otros: ver=0, crear=0, editar=0, eliminar=0
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'data' / 'dev.sqlite3'

def configure_auxiliar_permissions():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    try:
        # ID del rol Auxiliar
        AUXILIAR_ROLE_ID = 2
        
        # Permisos: Administración (5), Enrolar (2), Reportes (4) = ver sólo
        # Configuración (1), Seguridad (3) = sin permisos
        
        permissions_config = [
            (1, 0, 0, 0, 0),  # Configuración: sin acceso
            (2, 1, 0, 0, 0),  # Enrolar: solo ver
            (3, 0, 0, 0, 0),  # Seguridad: sin acceso
            (4, 1, 0, 0, 0),  # Reportes: solo ver
            (5, 1, 0, 0, 0),  # Administración: solo ver
        ]
        
        for permiso_id, ver, crear, editar, eliminar in permissions_config:
            # Verificar si ya existe
            cur.execute(
                "SELECT id FROM detalle_del_permiso WHERE rol_id = ? AND permiso_id = ?",
                (AUXILIAR_ROLE_ID, permiso_id)
            )
            existing = cur.fetchone()
            
            if existing:
                # Actualizar
                cur.execute(
                    """UPDATE detalle_del_permiso 
                       SET ver=?, crear=?, editar=?, eliminar=?, estado=1
                       WHERE rol_id=? AND permiso_id=?""",
                    (ver, crear, editar, eliminar, AUXILIAR_ROLE_ID, permiso_id)
                )
                print(f"✓ Actualizado: Permiso {permiso_id} - Ver:{ver}, Crear:{crear}, Editar:{editar}, Eliminar:{eliminar}")
            else:
                # Insertar
                cur.execute(
                    """INSERT INTO detalle_del_permiso (rol_id, permiso_id, estado, ver, crear, editar, eliminar)
                       VALUES (?, ?, 1, ?, ?, ?, ?)""",
                    (AUXILIAR_ROLE_ID, permiso_id, ver, crear, editar, eliminar)
                )
                print(f"✓ Creado: Permiso {permiso_id} - Ver:{ver}, Crear:{crear}, Editar:{editar}, Eliminar:{eliminar}")
        
        conn.commit()
        print("\n✅ Permisos del rol Auxiliar configurados correctamente.")
        
        # Mostrar resumen
        print("\nResumen de permisos del rol Auxiliar:")
        cur.execute("""
            SELECT p.id, p.nombre, d.ver, d.crear, d.editar, d.eliminar
            FROM detalle_del_permiso d
            JOIN permisos p ON d.permiso_id = p.id
            WHERE d.rol_id = ?
            ORDER BY p.id
        """, (AUXILIAR_ROLE_ID,))
        
        for row in cur.fetchall():
            flags = []
            if row['ver']: flags.append('Ver')
            if row['crear']: flags.append('Crear')
            if row['editar']: flags.append('Editar')
            if row['eliminar']: flags.append('Eliminar')
            flag_str = ', '.join(flags) if flags else 'SIN ACCESO'
            print(f"  {row['nombre']}: {flag_str}")
        
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    configure_auxiliar_permissions()
