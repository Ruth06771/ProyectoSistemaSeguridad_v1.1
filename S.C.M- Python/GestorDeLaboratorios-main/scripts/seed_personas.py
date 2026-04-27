#!/usr/bin/env python3
"""
Script pequeño para insertar 10 registros de prueba en la tabla `personas`.
Ejecutar desde la carpeta del proyecto backend:

    python scripts\seed_personas.py

El script evita duplicar entradas si ya existe el mismo `documento_identidad`.
"""
import random
import sys
import os
from pathlib import Path
from datetime import datetime

# Ensure the project package root is on sys.path so `import config` works
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.db import get_connection

SAMPLE_ROLES = ["Administrador", "Docente", "Estudiante", "Invitado"]
SAMPLE_SEX = ["M", "F", "O"]

persons = []
for i in range(1, 11):
    persons.append({
        "nombre_completo": f"Persona Prueba {i}",
        "fecha_nacimiento": (datetime(1990 + (i % 20), 1 + (i % 12), 1 + (i % 27))).strftime("%Y-%m-%d"),
        "correo": f"prueba{i}@ueb.edu.bo",
        "telefono_personal": f"+591700000{i:02d}",
        "documento_identidad": f"PTEST{i:04d}",
        "sexo": random.choice(SAMPLE_SEX),
        "tipo_sangre": None,
        "rol": random.choice(SAMPLE_ROLES),
        "estado": 1,
        "persona_emergencia": None,
        "telefono_emergencia": None,
    })


def insert_person(conn, p):
    cur = conn.cursor()
    # check duplicate by documento_identidad
    cur.execute("SELECT id FROM personas WHERE documento_identidad = ?", (p['documento_identidad'],))
    r = cur.fetchone()
    if r:
        return r[0], False
    sql = (
        "INSERT INTO personas (nombre_completo, fecha_nacimiento, correo, telefono_personal, documento_identidad, sexo, tipo_sangre, rol, estado, persona_emergencia, telefono_emergencia)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    cur.execute(sql, (
        p['nombre_completo'], p['fecha_nacimiento'], p['correo'], p['telefono_personal'], p['documento_identidad'],
        p['sexo'], p['tipo_sangre'], p['rol'], p['estado'], p['persona_emergencia'], p['telefono_emergencia']
    ))
    conn.commit()
    return cur.lastrowid, True


def main():
    conn = get_connection()
    inserted = []
    skipped = []
    try:
        for p in persons:
            pid, created = insert_person(conn, p)
            if created:
                inserted.append((pid, p['nombre_completo']))
            else:
                skipped.append((pid, p['nombre_completo']))
    finally:
        conn.close()

    print(f"Inserted: {len(inserted)}")
    for pid, name in inserted:
        print(f"  id={pid} name={name}")
    if skipped:
        print(f"Skipped (already existed): {len(skipped)}")
        for pid, name in skipped:
            print(f"  id={pid} name={name}")


if __name__ == '__main__':
    main()
