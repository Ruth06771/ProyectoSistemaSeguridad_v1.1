from config.db import get_connection
conn = get_connection()
cur = conn.cursor()
try:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    rows = cur.fetchall()
    print('TABLES_COUNT', len(rows))
    for r in rows:
        # sqlite3.Row with single column 'name'
        try:
            print(r['name'])
        except Exception:
            print(r[0])
finally:
    try:
        cur.close()
    except:
        pass
    conn.close()
