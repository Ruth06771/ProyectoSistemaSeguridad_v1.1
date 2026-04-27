import React, { useState, useEffect } from 'react';

export default function AccesosHistorial({ onFiltrar, resultados = [], filtros = {}, onExportExcel, onExportPDF, onVolver }) {
  const [form, setForm] = useState(filtros);

  // If mounted with initial filtros, request data immediately so the table is populated
  useEffect(() => {
    if (onFiltrar) onFiltrar(filtros || {});
  }, []);

  const handleChange = e => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = e => {
    e.preventDefault();
    if (onFiltrar) onFiltrar(form);
  };

  return (
    <div className="container mt-4">
      <h2>Reporte de Historial de Accesos</h2>
      <div className="text-start mb-3">
        <button className="btn btn-outline-secondary" onClick={onVolver}>
          ← Volver al Módulo de Reportes
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
          <label className="form-label">Tipo de Acción</label>
          <select className="form-select" name="tipo_accion" value={form.tipo_accion || ''} onChange={handleChange}>
            <option value="">-- Todos --</option>
            <option value="alta">Alta</option>
            <option value="baja">Baja</option>
            <option value="acceso permitido">Acceso Permitido</option>
            <option value="acceso denegado">Acceso Denegado</option>
          </select>
        </div>
        <div className="col-md-2">
          <label className="form-label">Usuario Responsable</label>
          <input type="text" className="form-control" name="usuario_responsable" value={form.usuario_responsable || ''} onChange={handleChange} placeholder="Nombre o usuario" />
        </div>
        <div className="col-md-2">
          <label className="form-label">Tarjeta RFID</label>
          <input type="text" className="form-control" name="tarjeta" value={form.tarjeta || ''} onChange={handleChange} placeholder="ID o código" />
        </div>
        <div className="col-12 d-flex gap-2">
          <button className="btn btn-primary">🔍 Filtrar</button>
          <button type="button" className="btn btn-secondary" onClick={() => { setForm({}); if (onFiltrar) onFiltrar({}); }}>🔄 Limpiar</button>
          <button type="button" className="btn btn-success" onClick={onExportExcel}>📥 Exportar a Excel</button>
          <button type="button" className="btn btn-danger" onClick={onExportPDF}>📄 Exportar a PDF</button>
        </div>
      </form>
      <table className="table table-striped table-bordered table-hover">
        <thead className="table-dark">
          <tr>
            <th>ID</th>
            <th>Fecha y Hora</th>
            <th>Acción</th>
            <th>Usuario Responsable</th>
            <th>Tarjeta RFID</th>
          </tr>
        </thead>
        <tbody>
          {resultados.length > 0 ? resultados.map((row, i) => (
            <tr key={i}>
              <td>{row.id}</td>
              <td>{row.fecha_hora}</td>
              <td>{row.accion}</td>
              <td>{row.usuario_responsable}</td>
              <td>{row.tarjeta}</td>
            </tr>
          )) : (
            <tr><td colSpan={5} className="text-center">Sin resultados</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
