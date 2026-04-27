from pathlib import Path
p=Path(r'c:\Users\Server Tecnología\Pictures\Proyecto-en-Python-main\S.C.M- Python\GestorDeLaboratorios-main\modulos\reportes\accesos_historial.html')
s=p.read_text(encoding='utf-8')
print('counts: {{', s.count('{{'), '}}', s.count('}}'), '{%', s.count('{%'), '%}', s.count('%}'))
print('double quotes:', s.count('"'), 'single quotes:', s.count("'"))
print('style open/close', s.count('<style'), s.count('</style>'))
print('html open/close', s.count('<html'), s.count('</html>'))
# look for common template errors: '{{' without matching '}}' etc
if s.count('{{')!=s.count('}}'):
    print('MISMATCH in {{ }}')
if s.count('{%')!=s.count('%}'):
    print('MISMATCH in {% %}')
# check for unclosed tags minimally
open_tags = s.count('<div') - s.count('</div>')
print('div open minus close:', open_tags)