from config.db import get_connection

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT 1')
    print('DB OK, SELECT 1 =>', cur.fetchone())
    conn.close()
except Exception as e:
    print('DB connection failed:')
    import traceback
    traceback.print_exc()
