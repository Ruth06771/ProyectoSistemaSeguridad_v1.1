from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/reportes')
def reportes():
    return render_template('reportes.html')

# Rutas de ejemplo para los enlaces
@app.route('/admin')
def admin_dashboard():
    return "<h3>Panel de administrador</h3>"

@app.route('/accesos_historial')
def accesos_historial():
    return "<h3>Historial de Accesos</h3>"

@app.route('/tarjetas_historial')
def tarjetas_historial():
    return "<h3>Reporte de Altas y Bajas de Tarjetas RFID</h3>"

@app.route('/accesos_personal')
def accesos_personal():
    return "<h3>Reporte de Accesos Detallado por Usuario</h3>"

if __name__ == '__main__':
    app.run(debug=True)
