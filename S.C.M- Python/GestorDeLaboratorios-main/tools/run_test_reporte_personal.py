import traceback

try:
    import auth.login_api as login_api
    app = login_api.app
    # Use Flask test_request_context to emulate the request
    with app.test_request_context('/reporte_accesos_personal?fecha_desde=2025-01-01&fecha_hasta=2025-12-31'):
        from importlib import reload
        import modulos.reportes.exportar_pdf_personal as mod
        reload(mod)
        try:
            resp = mod.reporte_accesos_personal()
            try:
                print('Response type:', type(resp), 'status:', getattr(resp, 'status_code', 'n/a'))
            except Exception:
                print('Response returned:', resp)
        except Exception:
            traceback.print_exc()
except Exception:
    traceback.print_exc()
