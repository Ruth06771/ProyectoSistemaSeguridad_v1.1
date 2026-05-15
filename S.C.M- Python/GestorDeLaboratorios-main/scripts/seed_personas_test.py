"""
Script para poblar la base de datos con 8 registros de prueba realistas
para el módulo de historial de registro de personas.
"""
import sqlite3
from pathlib import Path
import sys
import os

# Asegurar que el directorio raíz esté en sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.db import get_connection

def seed_database():
    """Inserta datos de prueba realistas en la base de datos."""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Poblar tipos de sangre si no existen
        tipos_sangre = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        for tipo in tipos_sangre:
            cur.execute("INSERT OR IGNORE INTO tipo_sangre (nombre) VALUES (?)", (tipo,))

        # Poblar personas de emergencia si no existen
        personas_emergencia = [
            ('María González', 'Pérez', '78543210'),
            ('Carlos Rodríguez', 'López', '76543210'),
            ('Ana Martínez', 'García', '75543210'),
            ('Luis Sánchez', 'Fernández', '74543210'),
            ('Carmen Jiménez', 'Ruiz', '73543210'),
            ('José Moreno', 'Hernández', '72543210'),
            ('Isabel Muñoz', 'Díaz', '71543210'),
            ('Francisco Álvarez', 'Romero', '70543210')
        ]
        for nombres, apellidos, telefono in personas_emergencia:
            cur.execute("INSERT OR IGNORE INTO persona_emergencia (nombres, apellidos, telefono_personal) VALUES (?, ?, ?)",
                       (nombres, apellidos, telefono))

        # Obtener IDs de tipos de sangre y personas de emergencia
        cur.execute("SELECT id, nombre FROM tipo_sangre")
        tipos_sangre_dict = {row['nombre']: row['id'] for row in cur.fetchall()}

        cur.execute("SELECT id, nombres || ' ' || apellidos as nombre_completo FROM persona_emergencia")
        emergencias = cur.fetchall()

        # Datos de prueba realistas para personas (estudiantes/profesores de UEB)
        personas_data = [
            {
                'nombre_completo': 'Juan Carlos Pérez López',
                'fecha_nacimiento': '1995-03-15',
                'correo': 'juan.perez@ueb.edu.bo',
                'telefono_personal': '71234567',
                'documento_identidad': '12345678',
                'sexo': 'M',
                'tipo_sangre': tipos_sangre_dict['A+'],
                'rol': 'estudiante',
                'persona_emergencia': emergencias[0]['id'],
                'telefono_emergencia': '78543210'
            },
            {
                'nombre_completo': 'María Elena García Rodríguez',
                'fecha_nacimiento': '1998-07-22',
                'correo': 'maria.garcia@ueb.edu.bo',
                'telefono_personal': '72345678',
                'documento_identidad': '23456789',
                'sexo': 'F',
                'tipo_sangre': tipos_sangre_dict['O+'],
                'rol': 'estudiante',
                'persona_emergencia': emergencias[1]['id'],
                'telefono_emergencia': '76543210'
            },
            {
                'nombre_completo': 'Carlos Alberto Martínez Sánchez',
                'fecha_nacimiento': '1992-11-08',
                'correo': 'carlos.martinez@ueb.edu.bo',
                'telefono_personal': '73456789',
                'documento_identidad': '34567890',
                'sexo': 'M',
                'tipo_sangre': tipos_sangre_dict['B+'],
                'rol': 'docente',
                'persona_emergencia': emergencias[2]['id'],
                'telefono_emergencia': '75543210'
            },
            {
                'nombre_completo': 'Ana Patricia López Fernández',
                'fecha_nacimiento': '1997-05-30',
                'correo': 'ana.lopez@ueb.edu.bo',
                'telefono_personal': '74567890',
                'documento_identidad': '45678901',
                'sexo': 'F',
                'tipo_sangre': tipos_sangre_dict['AB+'],
                'rol': 'estudiante',
                'persona_emergencia': emergencias[3]['id'],
                'telefono_emergencia': '74543210'
            },
            {
                'nombre_completo': 'Luis Miguel Jiménez Torres',
                'fecha_nacimiento': '1990-09-12',
                'correo': 'luis.jimenez@ueb.edu.bo',
                'telefono_personal': '75678901',
                'documento_identidad': '56789012',
                'sexo': 'M',
                'tipo_sangre': tipos_sangre_dict['A-'],
                'rol': 'docente',
                'persona_emergencia': emergencias[4]['id'],
                'telefono_emergencia': '73543210'
            },
            {
                'nombre_completo': 'Carmen Rosa Moreno Díaz',
                'fecha_nacimiento': '1999-01-25',
                'correo': 'carmen.moreno@ueb.edu.bo',
                'telefono_personal': '76789012',
                'documento_identidad': '67890123',
                'sexo': 'F',
                'tipo_sangre': tipos_sangre_dict['B-'],
                'rol': 'estudiante',
                'persona_emergencia': emergencias[5]['id'],
                'telefono_emergencia': '72543210'
            },
            {
                'nombre_completo': 'José Antonio Muñoz Ramírez',
                'fecha_nacimiento': '1988-12-03',
                'correo': 'jose.munoz@ueb.edu.bo',
                'telefono_personal': '77890123',
                'documento_identidad': '78901234',
                'sexo': 'M',
                'tipo_sangre': tipos_sangre_dict['O-'],
                'rol': 'docente',
                'persona_emergencia': emergencias[6]['id'],
                'telefono_emergencia': '71543210'
            },
            {
                'nombre_completo': 'Isabel Cristina Álvarez Morales',
                'fecha_nacimiento': '1996-08-18',
                'correo': 'isabel.alvarez@ueb.edu.bo',
                'telefono_personal': '78901234',
                'documento_identidad': '89012345',
                'sexo': 'F',
                'tipo_sangre': tipos_sangre_dict['AB-'],
                'rol': 'estudiante',
                'persona_emergencia': emergencias[7]['id'],
                'telefono_emergencia': '70543210'
            }
        ]

        # Insertar personas
        for persona in personas_data:
            cur.execute("""
                INSERT OR IGNORE INTO personas (
                    nombre_completo, fecha_nacimiento, correo, telefono_personal,
                    documento_identidad, sexo, tipo_sangre, rol, estado,
                    persona_emergencia, telefono_emergencia
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (
                persona['nombre_completo'], persona['fecha_nacimiento'], persona['correo'],
                persona['telefono_personal'], persona['documento_identidad'], persona['sexo'],
                persona['tipo_sangre'], persona['rol'], persona['persona_emergencia'],
                persona['telefono_emergencia']
            ))

        conn.commit()
        print("✅ Base de datos poblada exitosamente con 8 registros de prueba realistas.")
        print("   - Tipos de sangre: 8 registros")
        print("   - Personas de emergencia: 8 registros")
        print("   - Personas registradas: 8 registros")

    except Exception as e:
        print(f"❌ Error al poblar la base de datos: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    seed_database()