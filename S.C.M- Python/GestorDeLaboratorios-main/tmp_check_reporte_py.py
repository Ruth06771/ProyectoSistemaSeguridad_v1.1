import auth.login_api as appmod
app = appmod.app
app.testing = True
with app.test_client() as client:
    tests = [
        '/reporte_tarjetas',
        '/reporte_tarjetas?fecha_desde=2024-01-01&fecha_hasta=2024-12-31&accion=alta&usuario=test&tarjeta=abc',
        '/exportar_excel_tarjetas',
        '/exportar_excel_tarjetas?fecha_desde=2024-01-01&fecha_hasta=2024-12-31&usuario=test&tarjeta=abc',
    ]
    for url in tests:
        res = client.get(url)
        data = res.get_data()
        print('URL', url)
        print('status', res.status_code)
        print('content-type', res.headers.get('Content-Type'))
        print('content-disposition', res.headers.get('Content-Disposition'))
        print('len', len(data))
        print('first10', data[:10])
        print('is_pdf', data[:4] == b'%PDF', 'is_xlsx', data[:4] == b'PK\x03\x04')
        print('---')
