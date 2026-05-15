import sqlite3
import json

conn = sqlite3.connect('data/dev.sqlite3')
cur = conn.cursor()
sql = '''
SELECT ha.id, p.documento_identidad, p.nombre_completo, ha.fecha_hora, ha.usuario, ha.accion
FROM historial_acciones ha
JOIN personas p ON ha.entidad_id = p.id
WHERE ha.entidad_tipo = 'persona'
ORDER BY ha.fecha_hora DESC, p.nombre_completo ASC
LIMIT 20
'''
cur.execute(sql)
rows = cur.fetchall()
print('columns:', [d[0] for d in cur.description])
print(json.dumps(rows, ensure_ascii=False, indent=2))
conn.close()
