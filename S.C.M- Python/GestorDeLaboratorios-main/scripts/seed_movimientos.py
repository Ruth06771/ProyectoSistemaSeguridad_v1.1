from config.db import get_connection

conn = get_connection()
cur = conn.cursor()
try:
    # Insert a movimiento de prueba
    cur.execute("INSERT INTO movimientos (nombre, tipo) VALUES (?, ?)", ("Movimiento de prueba", "entrada"))
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM movimientos")
    cnt = cur.fetchone()[0]
    print('movimientos count after insert:', cnt)
    cur.execute("SELECT id, nombre, tipo, fecha_hora FROM movimientos ORDER BY fecha_hora DESC LIMIT 5")
    rows = cur.fetchall()
    for r in rows:
        try:
            print(dict(r))
        except Exception:
            print(tuple(r))
finally:
    try:
        cur.close()
    except Exception:
        pass
    conn.close()
