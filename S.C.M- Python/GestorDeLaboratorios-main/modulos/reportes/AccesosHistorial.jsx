import React, { useState } from 'react';

export default function AccesosHistorial({ onFiltrar, resultados = [], filtros = {}, onExportExcel, onExportPDF, onVolver }) {
  const [form, setForm] = useState(filtros);

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
      <h2>Historial de Accesos</h2>
      <div className="text-start mb-3">
        <button className="btn btn-outline-secondary" onClick={onVolver}>
          ← Volver al Módulo de Reportes
        </button>
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
        <div className="col-12 d-flex gap-2">
          <button className="btn btn-primary">🔍 Filtrar</button>
          <button type="button" className="btn btn-secondary" onClick={() => { setForm({}); if (onFiltrar) onFiltrar({}); }}>🔄 Limpiar</button>
          <button type="button" className="btn btn-success" onClick={onExportExcel}>📥 Exportar a Excel</button>
          <button type="button" className="btn btn-danger" onClick={onExportPDF}>📄 Exportar a PDF</button>
        </div>
      </form>
      <div className="table-responsive">
        <table className="table table-striped table-bordered table-hover">
          <thead className="table-dark">
            <tr>
              <th>ID</th>
              <th>Fecha y Hora</th>
              <th>Persona</th>
              <th>Movimiento</th>
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
              <tr><td colSpan={6} className="text-center">Sin resultados</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
