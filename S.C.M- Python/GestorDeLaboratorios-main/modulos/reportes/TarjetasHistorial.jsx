import React, { useState } from 'react';

export default function TarjetasHistorial({ onFiltrar, resultados = [], filtros = {}, onExportExcel, onExportPDF, onVolver }) {
  const [form, setForm] = useState(filtros);

  const handleChange = e => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = e => {
    e.preventDefault();
    if (onFiltrar) onFiltrar(form);
  };

  const downloadFile = (url) => {
    return fetch(url, { credentials: 'include' })
      .then(async (res) => {
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
        return true;
      });
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

  const escapeHtml = (unsafe) => {
    return unsafe
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  };

  const handleExportPDF = () => {
    const params = new URLSearchParams(form).toString();
    downloadFile(`/reporte_tarjetas?${params}`).catch(() => {});
  };

  const handleExportExcel = () => {
    const params = new URLSearchParams(form).toString();
    downloadFile(`/exportar_excel_tarjetas?${params}`).catch(() => {});
  };

  const normalizeActionValue = value => {
    if (value === undefined || value === null) return '';
    return String(value).trim().toLowerCase();
  };

  const getAccionLabel = row => {
    const raw = normalizeActionValue(row.accion || row.tipo || row.movimiento || row.estado || row.estatus || row.estado_tarjeta || row.estado_actual);
    if (['alta', 'creada', 'create', 'created', 'activo', 'activated', 'activado', '1', 'true'].includes(raw)) return 'Alta';
    if (['baja', 'inactivo', 'desactivado', 'desactivada', 'inactive', 'desactivate', '0', 'false'].includes(raw)) return 'Baja';
    if (['editada', 'editado', 'edicion', 'edición', 'editar', 'update', 'updated', 'modificada', 'modificado'].includes(raw)) return 'Editada';
    if (['eliminada', 'eliminado', 'eliminar', 'deleted', 'delete'].includes(raw)) return 'Eliminada';
    if (raw) return raw.charAt(0).toUpperCase() + raw.slice(1);
    return '-';
  };

  return (
    <div className="container mt-4">
      <h2>📇 Historial de Altas y Bajas de Tarjetas</h2>
      <div className="text-start mb-3">
        <button className="btn btn-outline-secondary" onClick={onVolver} title="Regresar al panel de reportes">
          <span className="me-1">←</span> Volver al Módulo de Reportes
        </button>
      </div>
      <form className="row g-3 mb-4" onSubmit={handleSubmit}>
        <div className="col-md-3">
          <label className="form-label">Fecha Desde</label>
          <input type="date" className="form-control" name="fecha_desde" value={form.fecha_desde || ''} onChange={handleChange} />
        </div>
        <div className="col-md-3">
          <label className="form-label">Fecha Hasta</label>
          <input type="date" className="form-control" name="fecha_hasta" value={form.fecha_hasta || ''} onChange={handleChange} />
        </div>
        <div className="col-md-2">
          <label className="form-label">Acción</label>
          <select className="form-select" name="accion" value={form.accion || ''} onChange={handleChange}>
            <option value="">-- Todas --</option>
            <option value="alta">Alta</option>
            <option value="baja">Baja</option>
          </select>
        </div>
        <div className="col-md-2">
          <label className="form-label">Responsable</label>
          <input type="text" className="form-control" name="usuario" value={form.usuario || ''} onChange={handleChange} placeholder="Usuario responsable" />
        </div>
        <div className="col-md-2">
          <label className="form-label">Tarjeta UID</label>
          <input type="text" className="form-control" name="tarjeta" value={form.tarjeta || ''} onChange={handleChange} placeholder="UID tarjeta" />
        </div>
        <div className="col-12 d-flex gap-2">
          <button className="btn btn-primary">🔍 Filtrar</button>
          <button type="button" className="btn btn-secondary" onClick={() => { setForm({}); if (onFiltrar) onFiltrar({}); }}>🔄 Limpiar</button>
          <button type="button" className="btn btn-success" onClick={handleExportExcel}>📥 Exportar a Excel</button>
          <button type="button" className="btn btn-danger" onClick={handleExportPDF}>📄 Exportar a PDF</button>
        </div>
      </form>
      <table className="table table-striped table-bordered table-hover">
        <thead className="table-dark">
          <tr>
            <th>ID</th>
            <th>UID Tarjeta</th>
            <th>Persona Asignada</th>
            <th>Responsable</th>
            <th>Acción</th>
            <th>Fecha y Hora</th>
          </tr>
        </thead>
        <tbody>
          {resultados.length > 0 ? resultados.map((row, i) => (
            <tr key={i}>
              <td>{row.id}</td>
              <td>{row.uid_tarjeta || row.uid || '-'}</td>
              <td>{row.nombre_usuario || row.nombre_completo || '-'}</td>
              <td>{row.responsable || row.ejecutado_por || '-'}</td>
              <td>{getAccionLabel(row)}</td>
              <td>{row.fecha_hora || '-'}</td>
            </tr>
          )) : (
            <tr><td colSpan={6} className="text-center">Sin resultados</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
