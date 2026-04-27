import React, { useState, useEffect } from 'react';

export default function ReportesIngresos({ onFiltrar, resultados = [], filtros = {}, onExportExcel, onExportPDF, onVolver }) {
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
    // Este componente muestra el historial de ingresos de personas,
    // por lo que debe usar el endpoint de accesos personales.
    window.open(`/reporte_accesos_personal?${params}`, '_blank');
  };

  useEffect(() => {
    if (onFiltrar) onFiltrar(filtros || {});
  }, []);

  return (
    <div className="container mt-4">
      <h2>📇 Historial de Ingresos de Personas</h2>
      <div className="text-start mb-3">
        <button
          className="btn btn-outline-secondary"
          onClick={onVolver}
          title="Regresar al panel de informes"
        >
          <span className="me-1">←</span> Volver al Módulo de Informes
        </button>
      </div>

      <form className="row g-3 mb-4" onSubmit={handleSubmit}>
        <div className="col-md-3">
          <label className="form-label">Fecha Desde</label>
          <input
            type="date"
            className="form-control"
            name="fecha_desde"
            value={form.fecha_desde || ''}
            onChange={handleChange}
          />
        </div>

        <div className="col-md-3">
          <label className="form-label">Fecha Hasta</label>
          <input
            type="date"
            className="form-control"
            name="fecha_hasta"
            value={form.fecha_hasta || ''}
            onChange={handleChange}
          />
        </div>

        <div className="col-md-2">
          <label className="form-label">Acción</label>
          <select
            className="form-select"
            name="accion"
            value={form.accion || ''}
            onChange={handleChange}
          >
            <option value="">-- Todas --</option>
            <option value="alta">Alta</option>
            <option value="baja">Baja</option>
          </select>
        </div>

        <div className="col-md-2">
          <label className="form-label">Responsable</label>
          <input
            type="text"
            className="form-control"
            name="usuario"
            value={form.usuario || ''}
            onChange={handleChange}
            placeholder="Usuario responsable"
          />
        </div>

        <div className="col-md-2">
          <label className="form-label">UID de la tarjeta</label>
          <input
            type="text"
            className="form-control"
            name="tarjeta"
            value={form.tarjeta || ''}
            onChange={handleChange}
            placeholder="UID tarjeta"
          />
        </div>

        <div className="col-12 d-flex gap-2">
          <button className="btn btn-primary" type="submit">🔍 Filtrar</button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => {
              setForm({});
              if (onFiltrar) onFiltrar({});
            }}
          >
            🔄 Limpiar
          </button>
          <button type="button" className="btn btn-success" onClick={onExportExcel}>
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
            <th>Identificación</th>
            <th>Tarjeta UID</th>
            <th>Nombre del Usuario</th>
            <th>Método</th>
            <th>Responsable</th>
            <th>Fecha y Hora</th>
          </tr>
        </thead>
        <tbody>
          {resultados.length > 0 ? (
            resultados.map((row, i) => (
              <tr key={i}>
                <td>{row.id}</td>
                <td>{row.uid_tarjeta}</td>
                <td>{row.nombre_usuario}</td>
                <td>{row.accion}</td>
                <td>{row.responsable}</td>
                <td>{row.fecha_hora}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={6} className="text-center">
                Sin resultados
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

