#!/usr/bin/env python3
"""
Script para actualizar los headers de PDFs y poner DOS logos en todas las páginas:
- ueb-logo.png a la izquierda
- techspot-logo.png a la derecha
Funciona directamente sobre los archivos Python, sin depender de replace literal.
"""

import os

# ----- NUEVO HEADER -----
new_header_lines = [
"def add_header(canvas, doc):",
"    from flask import current_app",
"    import os",
"    canvas.saveState()",
"    # Rutas absolutas a los logos",
"    logo_techspot = os.path.join(current_app.root_path, 'static', 'img', 'techspot-logo.png')",
"    logo_ueb = os.path.join(current_app.root_path, 'static', 'img', 'ueb-logo.png')",
"    # Logo izquierda (UEB)",
"    if os.path.exists(logo_ueb):",
"        try:",
"            canvas.drawImage(logo_ueb, 20, 700, width=60, height=60, preserveAspectRatio=True)",
"        except Exception as e:",
"            print(f'Error logo UEB: {e}')",
"    # Logo derecha (Techspot)",
"    if os.path.exists(logo_techspot):",
"        try:",
"            canvas.drawImage(logo_techspot, 530, 700, width=60, height=60, preserveAspectRatio=True)",
"        except Exception as e:",
"            print(f'Error logo Techspot: {e}')",
"    canvas.restoreState()",
]

# Archivos a actualizar
files = [
    r"modulos\reportes\exportar_pdf_tarjetas.py",
    r"modulos\reportes\exportar_pdf_personal.py"
]

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    skip = False
    for line in lines:
        if "def add_header(" in line:
            skip = True
        if not skip:
            new_lines.append(line)
        if skip and line.strip() == "canvas.restoreState()":
            skip = False  # Terminamos de saltar el viejo header
    
    # Insertamos el nuevo header al principio del archivo
    new_content = "".join(new_lines) + "\n" + "\n".join(new_header_lines) + "\n"

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Actualizado: {file_path}")

print("\n✅ Todos los archivos PDF ahora tendrán DOS logos en el header.")
