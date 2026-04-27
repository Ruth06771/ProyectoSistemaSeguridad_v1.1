from config.db import get_connection, log_action

conn = get_connection()
cur = conn.cursor()

# Insert tarjeta
try:
    cur.execute("INSERT INTO tarjetas (uid, nombre_completo, correo) VALUES (?, ?, ?)", ("TESTUID123", "Test User", "test@ueb.edu.bo"))
    conn.commit()
    print('Tarjeta insertada id=', cur.lastrowid)
except Exception as e:
    print('Error insert tarjeta:', e)

# Insert historial_tarjetas
try:
    cur.execute("INSERT INTO historial_tarjetas (tarjeta_id, uid, nombre_completo, accion, ejecutado_por, descripcion) VALUES (?, ?, ?, ?, ?, ?)",
                (cur.lastrowid if cur.lastrowid else None, "TESTUID123", "Test User", "alta", "script", "Prueba insert historial"))
    conn.commit()
    print('Historial insertado id=', cur.lastrowid)
except Exception as e:
    print('Error insert historial:', e)

# Read back
cur.execute('SELECT id, uid, nombre_completo, correo FROM tarjetas ORDER BY id DESC LIMIT 5')
print('\nTarjetas:')
for r in cur.fetchall():
    print(dict(r))

cur.execute('SELECT * FROM historial_tarjetas ORDER BY id DESC LIMIT 5')
print('\nHistorial tarjetas:')
for r in cur.fetchall():
    print(dict(r))

cur.close()
conn.close()
