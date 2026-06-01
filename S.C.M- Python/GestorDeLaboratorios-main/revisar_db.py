from config.db import get_connection

TARGET_UID = 'E3314E1C'
TARGET_ID = 22


def main():
    conn = get_connection()
    cur = conn.cursor()
    try:
        print('Buscando registros en tabla enrolar con tarjeta_uid =', TARGET_UID, 'o tarjeta_id =', TARGET_ID)
        cur.execute(
            'SELECT id, persona_id, tarjeta_id, tarjeta_uid, estado FROM enrolar WHERE tarjeta_uid = ? OR tarjeta_id = ? LIMIT 100',
            (TARGET_UID, TARGET_ID)
        )
        rows = cur.fetchall()
        if not rows:
            print('No se encontraron registros para esos valores.')
            return

        for idx, row in enumerate(rows, start=1):
            try:
                persona_id = row['persona_id']
                tarjeta_id = row['tarjeta_id']
                tarjeta_uid = row['tarjeta_uid']
                estado = row['estado']
            except Exception:
                persona_id = row[1]
                tarjeta_id = row[2]
                tarjeta_uid = row[3]
                estado = row[4]
            print(f"Registro {idx}:")
            print(f"  id: {row['id'] if hasattr(row, 'keys') and 'id' in row else row[0]}")
            print(f"  persona_id: {persona_id}")
            print(f"  tarjeta_id: {tarjeta_id}")
            print(f"  tarjeta_uid: {tarjeta_uid}")
            print(f"  estado: {estado}")
            print('')
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    main()
