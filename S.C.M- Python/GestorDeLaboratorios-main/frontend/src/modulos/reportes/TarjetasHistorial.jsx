import React, { useState, useEffect } from 'react';

export default function TarjetasHistorial({ onFiltrar, resultados = [], filtros = {}, onExportExcel, onExportPDF, onVolver }) {
  const [form, setForm] = useState(filtros);
  const [loading, setLoading] = useState(false);

  // Cargar datos al montar el componente
  useEffect(() => {
    if (onFiltrar && Object.keys(resultados).length === 0) {
      setLoading(true);
      onFiltrar(form);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setForm(filtros || {});
  }, [filtros]);

  const handleChange = e => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = e => {
    e.preventDefault();
    if (onFiltrar) onFiltrar(form);
  };

  const handleExportPDF = () => {
    const params = new URLSearchParams(form).toString();
    window.open(`/reporte_tarjetas?${params}`, '_blank');
  };

  const handleExportExcel = () => {
    const params = new URLSearchParams(form).toString();
    window.open(`/exportar_excel_tarjetas?${params}`, '_blank');
  };

  const formatEstado = value => {
    if (value === 1 || value === '1' || value === true || value === 'Activo' || value === 'activo') return 'Activo';
    if (value === 0 || value === '0' || value === false) return 'Inactivo';
    return value || '-';
  };

  return (
    <div className="container mt-4">
      <h2>📇 Historial de Enrolamiento</h2>
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
        <div className="col-md-3">
          <label className="form-label">Acción</label>
          <select className="form-select" name="accion" value={form.accion || ''} onChange={handleChange}>
            <option value="">-- Todas --</option>
            <option value="activo">Activo</option>
            <option value="inactivo">Inactivo</option>
            <option value="eliminado">Eliminado</option>
            <option value="editado">Editado</option>
          </select>
        </div>
        <div className="col-md-3">
          <label className="form-label">Persona</label>
          <input type="text" className="form-control" name="persona" value={form.persona || ''} onChange={handleChange} placeholder="Nombre de la persona" />
        </div>
        <div className="col-md-3">
          <label className="form-label">Tarjeta UID</label>
          <input type="text" className="form-control" name="tarjeta" value={form.tarjeta || ''} onChange={handleChange} placeholder="UID tarjeta" />
        </div>
        <div className="col-12 d-flex gap-2 flex-wrap">
          <button className="btn btn-primary">🔍 Filtrar</button>
          <button type="button" className="btn btn-outline-secondary" onClick={() => { setLoading(true); if (onFiltrar) { onFiltrar(form); setTimeout(() => setLoading(false), 500); } }}>
            {loading ? '⏳ Actualizando...' : '🔄 Actualizar'}
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => { setForm({}); setLoading(true); if (onFiltrar) { onFiltrar({}); setTimeout(() => setLoading(false), 500); } }}>
            🧹 Limpiar
          </button>
          <button type="button" className="btn btn-success" onClick={handleExportExcel}>
            📥 Exportar a Excel
          </button>
          <button type="button" className="btn btn-danger" onClick={handleExportPDF}>
            📄 Exportar a PDF
          </button>
        </div>
      </form>
      <table className="table table-striped table-bordered table-hover">
        <thead className="table-dark">
          <tr>
            <th>ID</th>
            <th>Nombre de la Persona</th>
            <th>Tarjeta UID</th>
            <th>PIN</th>
            <th>Perfil</th>
            <th>Acción</th>
            <th>Responsable</th>
            <th>Fecha y Hora</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {resultados.length > 0 ? resultados.map((row, i) => (
            <tr key={i}>
              <td>{row.id || '-'}</td>
              <td>{row.nombre_usuario || row.nombre_completo || row.nombre || '-'}</td>
              <td>{row.tarjeta_uid || row.uid_tarjeta || row.uid || '-'}</td>
              <td>{row.pin || '-'}</td>
              <td>{row.perfil || '-'}</td>
              <td>
                <span className={`badge ${row.accion === 'activo' ? 'bg-success' : row.accion === 'inactivo' ? 'bg-warning' : row.accion === 'eliminado' ? 'bg-danger' : 'bg-secondary'}`}>
                  {row.accion || '-'}
                </span>
              </td>
              <td>{row.responsable || row.ejecutado_por || '-'}</td>
              <td>{row.fecha_hora || row.fecha_de_registro || '-'}</td>
              <td>{formatEstado(row.estado)}</td>
            </tr>
          )) : (
            <tr><td colSpan={9} className="text-center">Sin resultados</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
