from importlib import import_module
print('IMPORT_REPORTLAB:', end=' ')
try:
    import reportlab
    print('OK', reportlab.Version)
except Exception as e:
    print('FAIL', type(e).__name__, e)

print('IMPORT_BLUEPRINT_MODULE:', end=' ')
try:
    m = import_module('modulos.reportes.exportar_pdf_tarjetas')
    print('OK')
except Exception as e:
    print('FAIL', type(e).__name__, e)

# Generar PDF de prueba
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
fn = 'prueba_reportlab_proyecto.pdf'
try:
    c = canvas.Canvas(fn, pagesize=letter)
    c.drawString(100, 700, 'Prueba ReportLab desde el proyecto')
    c.save()
    print('PDF_CREATED', fn)
except Exception as e:
    print('PDF_FAIL', type(e).__name__, e)
