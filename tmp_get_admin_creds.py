import sqlite3
import os

path = 'S.C.M- Python/GestorDeLaboratorios-main/data/dev.sqlite3'
conn = sqlite3.connect(path)
cursor = conn.cursor()

# Get admin user
cursor.execute("SELECT * FROM usuario WHERE email LIKE '%admin%' LIMIT 1")
row = cursor.fetchone()
print("Admin user:", row)

# Get all columns for reference
cursor.execute("PRAGMA table_info(usuario)")
columns = cursor.fetchall()
print("\nUsuario table columns:")
for col in columns:
    print(f"  {col[0]}: {col[1]} ({col[2]})")

conn.close()
