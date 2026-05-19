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
    const nextForm = { ...form, [name]: value };
    setForm(nextForm);
    if (name === 'accion' && onFiltrar) {
      onFiltrar(nextForm);
    }
  };

  const handleSubmit = e => {
    e.preventDefault();
    if (onFiltrar) onFiltrar(form);
  };

  const openDownload = (url) => {
    const link = document.createElement('a');
    link.href = url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportPDF = () => {
    if (onExportPDF) {
      onExportPDF(form);
      return;
    }
    const params = new URLSearchParams(form).toString();
    openDownload(`/reporte_tarjetas?${params}`);
  };

  const handleExportExcel = () => {
    if (onExportExcel) {
      onExportExcel(form);
      return;
    }
    const params = new URLSearchParams(form).toString();
    openDownload(`/exportar_excel_tarjetas?${params}`);
  };

  const formatEstado = value => {
    if (value === 1 || value === '1' || value === true || value === 'Activo' || value === 'activo') return 'Activo';
    if (value === 0 || value === '0' || value === false || value === 'Inactivo' || value === 'inactivo') return 'Inactivo';
    return value || '-';
  };

  const normalizeActionValue = value => {
    if (value === undefined || value === null) return '';
    return String(value).trim().toLowerCase();
  };

  const getAccionLabel = row => {
    const rawValue = row.accion || row.tipo || row.movimiento || row.estado || row.estatus || row.estado_tarjeta || row.estado_actual || row.descripcion || '';
    const accion = normalizeActionValue(rawValue);
    if (accion === 'alta' || accion === 'activo' || accion === 'activado' || accion === '1' || accion === 'true' || accion === 'creada') return 'Alta';
    if (accion === 'baja' || accion === 'inactivo' || accion === 'desactivado' || accion === '0' || accion === 'false') return 'Baja';
    if (accion === 'editada' || accion === 'editado' || accion === 'edicion' || accion === 'edición' || accion === 'editar' || accion === 'edit' || accion.includes('edit')) return 'Editada';
    if (accion === 'eliminada' || accion === 'eliminado' || accion === 'eliminar' || accion === 'borrada' || accion === 'borrado' || accion.includes('elim')) return 'Eliminada';
    if (accion === 'sin cambio' || accion === 'sincambio' || accion === 'no cambio' || accion === 'nocambio') return 'Sin cambio';
    if (accion === 'modificada' || accion.includes('modific')) return 'Editada';
    if (accion) return accion.charAt(0).toUpperCase() + accion.slice(1);
    return '-';
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
            <option value="alta">Alta</option>
            <option value="baja">Baja</option>
            <option value="editada">Editada</option>
            <option value="eliminada">Eliminada</option>
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
            <th>Persona</th>
            <th>Perfil</th>
            <th>Credenciales</th>
            <th>Estado</th>
            <th>Responsable</th>
            <th>Fecha y Hora</th>
          </tr>
        </thead>
        <tbody>
          {resultados.length > 0 ? resultados.map((row, i) => {
            const persona = row.nombre_persona || row.persona || '-';
            const perfil = row.perfil || '-';
            const uid = row.tarjeta_uid || row.uid_tarjeta || row.uid || '-';
            const pin = row.tarjeta_pin || row.pin || '-';
            const estado = row.estado || row.accion || row.tipo || '-';
            const responsable = row.responsable || row.ejecutado_por || 'Sistema';
            const fecha = row.fecha_hora || row.fecha_de_registro || '-';
            return (
              <tr key={i}>
                <td>{row.id || '-'}</td>
                <td>{persona}</td>
                <td>{perfil}</td>
                <td>{`UID: ${uid} / PIN: ${pin}`}</td>
                <td>{estado}</td>
                <td>{responsable}</td>
                <td>{fecha}</td>
              </tr>
            );
          }) : (
            <tr><td colSpan={7} className="text-center">Sin resultados</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
