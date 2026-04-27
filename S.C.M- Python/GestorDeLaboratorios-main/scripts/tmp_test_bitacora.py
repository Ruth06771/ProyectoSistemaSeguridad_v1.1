import requests
base='http://127.0.0.1:5000'
# create tarjeta
r1 = requests.post(base+'/api/tarjetas', json={'uid':'BIT_TEST_UID','nombre_completo':'Bit Test','correo':'bit@test.local'})
print('tarjeta POST', r1.status_code, r1.text)
# create persona
r2 = requests.post(base+'/api/personas', json={'nombre_completo':'Bit Persona','fecha_nacimiento':'1990-01-01','correo':'bit@person.local','telefono_personal':'123','documento_identidad':'ID123','sexo':'Otro','tipo_sangre':'O+','rol':'estudiante','persona_emergencia':'Contacto','telefono_emergencia':'321'})
print('persona POST', r2.status_code, r2.text)
# get bitacora
r3 = requests.get(base+'/api/bitacora')
print('bitacora status', r3.status_code)
data = r3.json()
print('last 10 entries:')
for row in data[:10]:
    print(row)
