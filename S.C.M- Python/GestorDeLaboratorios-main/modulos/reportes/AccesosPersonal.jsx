import React, { useState } from 'react';

export default function AccesosPersonal({ onFiltrar, resultados = [], filtros = {}, onExportExcel, onExportPDF, onVolver }) {
  const [form, setForm] = useState(filtros);

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
    window.open(`/reporte_accesos_personal?${params}`, '_blank');
  };

  return (
    <div className="p-4">
      <h2 className="mb-4">📌 Reporte de Accesos Detallado</h2>
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
          <label className="form-label">Movimiento</label>
          <select name="tipo_movimiento" className="form-select" value={form.tipo_movimiento || ''} onChange={handleChange}>
            <option value="">-- Todos --</option>
            <option value="acceso permitido">Acceso Permitido</option>
            <option value="acceso denegado">Acceso Denegado</option>
            <option value="salida">Salida</option>
          </select>
        </div>
        <div className="col-md-2">
          <label className="form-label">Nombre</label>
          <input type="text" name="nombre_completo" className="form-control" value={form.nombre_completo || ''} onChange={handleChange} />
        </div>
        <div className="col-md-2">
          <label className="form-label">UID Tarjeta</label>
          <input type="text" name="uid_tarjeta" className="form-control" value={form.uid_tarjeta || ''} onChange={handleChange} />
        </div>
        <div className="col-12 d-flex gap-2 mt-2">
          <button className="btn btn-primary">🔍 Filtrar</button>
          <button type="button" className="btn btn-secondary" onClick={() => { setForm({}); if (onFiltrar) onFiltrar({}); }}>🔄 Limpiar</button>
          <button type="button" className="btn btn-success" onClick={onExportExcel}>📥 Exportar a Excel</button>
          <button type="button" className="btn btn-danger" onClick={handleExportPDF}>📄 Exportar a PDF</button>
        </div>
      </form>
      <table className="table table-bordered table-hover">
        <thead className="table-dark">
          <tr>
            <th>ID</th>
            <th>Fecha y Hora</th>
            <th>Movimiento</th>
            <th>Nombre</th>
            <th>Documento</th>
            <th>UID Tarjeta</th>
            <th>Registrado Por</th>
            <th>Descripción</th>
          </tr>
        </thead>
        <tbody>
          {resultados.length > 0 ? resultados.map((row, i) => (
            <tr key={i}>
              <td>{row.id}</td>
              <td>{row.fecha_hora}</td>
              <td>{row.movimiento}</td>
              <td>{row.nombre}</td>
              <td>{row.documento}</td>
              <td>{row.uid_tarjeta}</td>
              <td>{row.registrado_por}</td>
              <td>{row.descripcion}</td>
            </tr>
          )) : (
            <tr><td colSpan={8} className="text-center">Sin resultados</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
