import React, { useState, useEffect } from 'react';

export default function AccesosHistorial({ onFiltrar, resultados = [], filtros = {}, onExportExcel, onExportPDF, onVolver }) {
  const [form, setForm] = useState(filtros);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [autoRefresh, setAutoRefresh] = useState(false);

  const escapeHtml = (unsafe) => {
    return unsafe
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  };

  const parseFilename = (contentDisposition, url, contentType, blobType) => {
    let filename = '';
    const match = /filename\*=UTF-8''([^;\n\r]+)/i.exec(contentDisposition) || /filename="?([^";]+)"?/i.exec(contentDisposition);
    if (match && match[1]) {
      try { filename = decodeURIComponent(match[1]); } catch (e) { filename = match[1]; }
    }
    if (!filename) {
      const type = contentType || blobType || '';
      if (type.includes('pdf')) filename = 'reporte.pdf';
      else if (type.includes('spreadsheet') || type.includes('excel')) filename = 'reporte.xlsx';
      else if (url.endsWith('.pdf')) filename = 'reporte.pdf';
      else if (url.includes('exportar_excel')) filename = 'reporte.xlsx';
      else filename = 'reporte';
    }
    return filename;
  };

  const downloadFile = async (url) => {
    const res = await fetch(url, { credentials: 'include' });
    if (!res.ok) {
      const text = await res.text();
      const w = window.open();
      if (w) {
        w.document.write('<pre>' + escapeHtml(text) + '</pre>');
        w.document.title = 'Error al exportar';
      } else {
        alert('Error al exportar: ' + res.status + ' ' + res.statusText);
      }
      throw new Error('Error al exportar');
    }
    const blob = await res.blob();
    const contentDisposition = res.headers.get('Content-Disposition') || '';
    const filename = parseFilename(contentDisposition, url, res.headers.get('Content-Type') || '', blob.type);
    const urlObj = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = urlObj;
    link.download = filename;
    link.target = '_blank';
    link.rel = 'noopener';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(urlObj);
  };

  const handleExportExcel = async () => {
    const params = new URLSearchParams(form).toString();
    if (onExportExcel) {
      return onExportExcel(form);
    }
    await downloadFile(`/exportar_excel_accesos?${params}`);
  };

  const handleExportPDF = async () => {
    const params = new URLSearchParams(form).toString();
    if (onExportPDF) {
      return onExportPDF(form);
    }
    await downloadFile(`/reporte_accesos_personal?${params}`);
  };

  // Sincronizar form cuando cambien los filtros desde el padre
  useEffect(() => {
    setForm(filtros || {});
  }, [filtros]);

  const handleChange = e => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = e => {
    e.preventDefault();
    handleRefresh(form);
  };

  const handleRefresh = (filterObj = form) => {
    setLoading(true);
    if (onFiltrar) {
      onFiltrar(filterObj);
    }
    setLastUpdate(new Date());
    setTimeout(() => setLoading(false), 500);
  };

  // Auto-refresco cada 10 segundos si está habilitado
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      handleRefresh(form);
    }, 10000); // 10 segundos

    return () => clearInterval(interval);
  }, [autoRefresh, form]);

  return (
    <div className="container mt-4">
      <h2>Historial de Accesos</h2>
      <div className="text-start mb-3">
        <button className="btn btn-outline-secondary" onClick={onVolver}>
          ← Volver al Módulo de Reportes
        </button>
      </div>
      
      {/* Barra de información */}
      <div className="alert alert-info d-flex justify-content-between align-items-center mb-3" role="alert">
        <span>
          📊 Últimas actualizaciones: <strong>{lastUpdate.toLocaleTimeString('es-ES')}</strong> | Total: <strong>{resultados.length}</strong> registros
        </span>
        <div className="form-check form-switch">
          <input 
            className="form-check-input" 
            type="checkbox" 
            id="autoRefreshSwitch"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
          />
          <label className="form-check-label" htmlFor="autoRefreshSwitch">
            🔄 Auto-actualizar (10s)
          </label>
        </div>
      </div>

      <form className="row g-3 mb-4" onSubmit={handleSubmit}>
        <div className="col-md-2">
          <label className="form-label">Fecha Desde</label>
          <input type="date" className="form-control" name="fecha_desde" value={form.fecha_desde || ''} onChange={handleChange} />
        </div>
        <div className="col-md-2">
          <label className="form-label">Fecha Hasta</label>
          <input type="date" className="form-control" name="fecha_hasta" value={form.fecha_hasta || ''} onChange={handleChange} />
        </div>
        <div className="col-md-2">
          <label className="form-label">Movimiento</label>
          <select className="form-select" name="tipo_movimiento" value={form.tipo_movimiento || ''} onChange={handleChange}>
            <option value="">-- Todos --</option>
            <option value="Entrada">Entrada</option>
            <option value="Salida">Salida</option>
          </select>
        </div>
        <div className="col-md-2">
          <label className="form-label">Resultado</label>
          <select className="form-select" name="resultado" value={form.resultado || ''} onChange={handleChange}>
            <option value="">-- Todos --</option>
            <option value="Permitido">Permitido</option>
            <option value="Denegado">Denegado</option>
          </select>
        </div>
        <div className="col-md-2">
          <label className="form-label">Credencial</label>
          <select className="form-select" name="credencial" value={form.credencial || ''} onChange={handleChange}>
            <option value="">-- Todos --</option>
            <option value="Tarjeta">Tarjeta</option>
            <option value="PIN">PIN</option>
          </select>
        </div>
        <div className="col-12 d-flex gap-2 flex-wrap">
          <button className="btn btn-primary" disabled={loading}>
            {loading ? '⏳ Cargando...' : '🔍 Filtrar'}
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => { setForm({}); handleRefresh({}); }} disabled={loading}>
            🔄 Limpiar
          </button>
          <button type="button" className="btn btn-info" onClick={() => handleRefresh(form)} disabled={loading}>
            ↻ Actualizar Ahora
          </button>
          <button type="button" className="btn btn-success" onClick={handleExportExcel} disabled={loading || resultados.length === 0}>
            📥 Exportar a Excel
          </button>
          <button type="button" className="btn btn-danger" onClick={handleExportPDF} disabled={loading || resultados.length === 0}>
            📄 Exportar a PDF
          </button>
        </div>
      </form>

      {/* Loading indicator */}
      {loading && (
        <div className="text-center mb-3">
          <div className="spinner-border spinner-border-sm text-primary" role="status">
            <span className="visually-hidden">Cargando...</span>
          </div>
          <span className="ms-2 text-muted">Actualizando datos...</span>
        </div>
      )}

      <div className="table-responsive">
        <table className="table table-striped table-bordered table-hover">
          <thead className="table-dark">
            <tr>
              <th>ID</th>
              <th>Fecha y Hora</th>
              <th>Persona</th>
              <th>Movimiento</th>
              <th>Acción ESP</th>
              <th>Resultado</th>
              <th>Credencial</th>
            </tr>
          </thead>
          <tbody>
            {resultados.length > 0 ? resultados.map((row, i) => (
              <tr key={i}>
                <td>{row.id}</td>
                <td>{row.fecha_hora}</td>
                <td>{row.persona}</td>
                <td>
                  <span className={`badge ${row.movimiento === 'Entrada' ? 'bg-success' : 'bg-info'}`}>
                    {row.movimiento}
                  </span>
                </td>
                <td>{row.accion || '-'}</td>
                <td>
                  <span className={`badge ${row.resultado === 'Permitido' ? 'bg-success' : 'bg-danger'}`}>
                    {row.resultado}
                  </span>
                </td>
                <td>
                  <span className={`badge ${row.credencial === 'Tarjeta' ? 'bg-primary' : 'bg-warning'}`}>
                    {row.credencial}
                  </span>
                </td>
              </tr>
            )) : (
              <tr><td colSpan={7} className="text-center text-muted">Sin resultados</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
