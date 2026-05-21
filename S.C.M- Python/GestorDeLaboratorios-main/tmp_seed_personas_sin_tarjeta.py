#!/usr/bin/env python3
"""
Script para insertar 5 personas de prueba que NO están enroladas (sin tarjeta).
Inserta registros en 'personas' y crea logs en 'historial_acciones'.
"""

import sys
import os
from datetime import datetime, timedelta

# Asegurar que el directorio raíz esté en sys.path
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.db import get_connection, log_action

# Datos de prueba: 5 personas que NO tendrán tarjeta
TEST_PERSONAS = [
    {
        'nombre_completo': 'Juan Carlos Ramírez López',
        'fecha_nacimiento': '1990-05-15',
        'correo': 'juan.ramirez@ueb.edu.bo',
        'telefono_personal': '591-76543210',
        'documento_identidad': '8945612',
        'sexo': 'Masculino',
        'tipo_sangre': 1,  # O+
        'rol': 'estudiante',
        'estado': 1,
        'usuario_registro': 'admin@ueb.edu.bo'
    },
    {
        'nombre_completo': 'María Elena Gutiérrez Silva',
        'fecha_nacimiento': '1988-03-22',
        'correo': 'maria.gutierrez@ueb.edu.bo',
        'telefono_personal': '591-77654321',
        'documento_identidad': '5234890',
        'sexo': 'Femenino',
        'tipo_sangre': 2,  # A+
        'rol': 'docente',
        'estado': 1,
        'usuario_registro': 'admin@ueb.edu.bo'
    },
    {
        'nombre_completo': 'Roberto Alejandro Flores Mendez',
        'fecha_nacimiento': '1992-07-10',
        'correo': 'roberto.flores@ueb.edu.bo',
        'telefono_personal': '591-78765432',
        'documento_identidad': '9876543',
        'sexo': 'Masculino',
        'tipo_sangre': 3,  # B+
        'rol': 'Auxiliar',
        'estado': 1,
        'usuario_registro': 'admin@ueb.edu.bo'
    },
    {
        'nombre_completo': 'Ana Patricia Morales Quintanilla',
        'fecha_nacimiento': '1995-11-08',
        'correo': 'ana.morales@ueb.edu.bo',
        'telefono_personal': '591-79876543',
        'documento_identidad': '4567890',
        'sexo': 'Femenino',
        'tipo_sangre': 4,  # AB+
        'rol': 'Auxiliar',
        'estado': 1,
        'usuario_registro': 'admin@ueb.edu.bo'
    },
    {
        'nombre_completo': 'Daniel Ernesto Pérez Castillo',
        'fecha_nacimiento': '1989-09-30',
        'correo': 'daniel.perez@ueb.edu.bo',
        'telefono_personal': '591-70123456',
        'documento_identidad': '1234567',
        'sexo': 'Masculino',
        'tipo_sangre': 1,  # O+
        'rol': 'Técnico',
        'estado': 1,
        'usuario_registro': 'admin@ueb.edu.bo'
    }
]


def seed_personas():
    """Inserta 5 personas de prueba con sus registros en historial_acciones."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        inserted_count = 0
        
        for persona in TEST_PERSONAS:
            usuario_registro = persona.pop('usuario_registro')
            
            # Insertar en tabla personas
            sql = """
            INSERT INTO personas 
            (nombre_completo, fecha_nacimiento, correo, telefono_personal, 
            documento_identidad, sexo, tipo_sangre, rol, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            valores = (
                persona['nombre_completo'],
                persona['fecha_nacimiento'],
                persona['correo'],
                persona['telefono_personal'],
                persona['documento_identidad'],
                persona['sexo'],
                persona['tipo_sangre'],
                persona['rol'],
                persona['estado']
            )
            
            cursor.execute(sql, valores)
            conn.commit()
            
            # Obtener el ID de la persona insertada
            persona_id = cursor.lastrowid
            
            # Crear registro en historial_acciones
            # Generar una fecha aleatoria en los últimos 7 días
            dias_atras = inserted_count % 7
            fecha_registro = (  - timedelta(days=dias_atras)).isoformat()
            
            log_action(
                conn,
                modulo='personas',
                entidad_id=persona_id,
                entidad_tipo='persona',
                accion='create',
                usuario=usuario_registro,
                descripcion=f"Persona registrada: {persona['nombre_completo']}"
            )
            
            inserted_count += 1
            print(f"✓ Persona insertada: {persona['nombre_completo']} (ID: {persona_id})")
        
        print(f"\n✅ Se han insertado exitosamente {inserted_count} personas de prueba.")
        print("\nDetalles de las personas insertadas:")
        print("─" * 80)
        
        # Mostrar un resumen de las personas insertadas
        cursor.execute("""
        SELECT 
            p.id,
            p.documento_identidad,
            p.nombre_completo,
            ha.fecha_hora,
            ha.usuario
        FROM personas p
        LEFT JOIN historial_acciones ha ON (
            p.id = ha.entidad_id 
            AND ha.entidad_tipo = 'persona' 
            AND ha.accion = 'create'
        )
        WHERE p.documento_identidad IN (?, ?, ?, ?, ?)
        ORDER BY p.id DESC
        """, (
            '8945612', '5234890', '9876543', '4567890', '1234567'
        ))
        
        rows = cursor.fetchall()
        for row in rows:
            row_dict = dict(row)
            print(f"ID: {row_dict['id']} | Cédula: {row_dict['documento_identidad']} | "
                  f"Nombre: {row_dict['nombre_completo']} | "
                  f"Registrado por: {row_dict['usuario']}")
        
        print("─" * 80)
        print("\n✅ Datos de prueba creados correctamente.")
        print("💡 Estas personas aparecerán en el reporte 'Historial de Registro de Personas'")
        print("   porque NO existen en la tabla 'enrolar' (no tienen tarjeta asignada).")
        
    except Exception as e:
        print(f"❌ Error al insertar personas: {str(e)}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    print("=" * 80)
    print("🌱 Semilla de Datos - Personas Sin Tarjeta")
    print("=" * 80)
    print()
    
    try:
        seed_personas()
    except Exception as e:
        print(f"\n❌ Falló la ejecución del script: {str(e)}")
        sys.exit(1)
