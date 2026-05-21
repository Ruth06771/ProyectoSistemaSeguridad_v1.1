import React, { useState, useEffect } from 'react';

export default function TarjetasHistorial({ onFiltrar, resultados = [], filtros = {}, onExportExcel, onExportPDF, onVolver }) {
  const [form, setForm] = useState(filtros);
  const [loading, setLoading] = useState(false);
  const [enrolarData, setEnrolarData] = useState([]);

  const loadEnrolarData = async () => {
    try {
      const res = await fetch('/api/enrolar', { credentials: 'include' });
      if (!res.ok) {
        setEnrolarData([]);
        return;
      }
      const data = await res.json();
      setEnrolarData(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error cargando personas enroladas:', err);
      setEnrolarData([]);
    }
  };

  useEffect(() => {
    if (onFiltrar && resultados.length === 0) {
      setLoading(true);
      Promise.resolve(onFiltrar(form)).finally(() => setLoading(false));
    }
    loadEnrolarData();
    const interval = setInterval(loadEnrolarData, 15000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setForm(filtros || {});
  }, [filtros]);

  const handleChange = e => {
    const { name, value } = e.target;
    const nextForm = { ...form, [name]: value };
    setForm(nextForm);
    if (name === 'accion' && onFiltrar) {
      setLoading(true);
      Promise.resolve(onFiltrar(nextForm)).finally(() => setLoading(false));
    }
  };

  const handleSubmit = async e => {
    e.preventDefault();
    if (!onFiltrar) return;
    setLoading(true);
    await Promise.resolve(onFiltrar(form));
    setLoading(false);
  };

  const handleActualizar = async () => {
    if (!onFiltrar) return;
    setLoading(true);
    await Promise.resolve(onFiltrar(form));
    setLoading(false);
  };

  const handleLimpiar = async () => {
    const emptyForm = {};
    setForm(emptyForm);
    if (!onFiltrar) return;
    setLoading(true);
    await Promise.resolve(onFiltrar(emptyForm));
    setLoading(false);
    await loadEnrolarData();
  };

  const getEnrolarRow = (row) => {
    if (!enrolarData || enrolarData.length === 0) return null;
    return enrolarData.find(item => item.id === row.enrolar_id || item.tarjeta_uid === row.tarjeta_uid || item.tarjeta_uid === row.uid_tarjeta);
  };

  const displayRows = resultados.length > 0 ? resultados : enrolarData;
  const showingEnrolarData = resultados.length === 0;

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

  const renderEstadoBadge = (rawEstado) => {
    const label = formatEstado(rawEstado);
    const normalized = normalizeActionValue(rawEstado);
    if (normalized === 'eliminado' || normalized === 'eliminada' || normalized === 'delete' || normalized === 'deleted') {
      return <span className="badge bg-danger">Eliminado</span>;
    }
    if (normalized === 'inactivo' || normalized === '0' || normalized === 'false') {
      return <span className="badge bg-warning text-dark">Inactivo</span>;
    }
    if (normalized === 'activo' || normalized === '1' || normalized === 'true') {
      return <span className="badge bg-success">Activo</span>;
    }
    return <span className="badge bg-secondary">{label}</span>;
  };

  return (
    <div className="container mt-4">
      <div className="d-flex align-items-baseline justify-content-between mb-2">
        <h2 className="mb-0">📇 Historial de Enrolamiento</h2>
        <small className="text-muted">Datos sincronizados con personas enroladas cada 15s</small>
      </div>
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
          <label className="form-label">Estado</label>
          <select className="form-select" name="accion" value={form.accion || ''} onChange={handleChange}>
            <option value="">-- Todas --</option>
            <option value="activo">Activo</option>
            <option value="inactivo">Inactivo</option>
            <option value="eliminado">Eliminado</option>
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
          <button type="button" className="btn btn-outline-secondary" onClick={handleActualizar}>
            {loading ? '⏳ Actualizando...' : '🔄 Actualizar'}
          </button>
          <button type="button" className="btn btn-secondary" onClick={handleLimpiar}>
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
            <th>Correo</th>
            <th>Documento</th>
            <th>Tipo sangre</th>
            <th>Perfil</th>
            <th>Tarjeta UID</th>
            <th>PIN</th>
            <th>Estado</th>
            <th>Acción</th>
            <th>Responsable</th>
            <th>Fecha y Hora</th>
          </tr>
        </thead>
        <tbody>
          {displayRows.length > 0 ? displayRows.map((row, i) => {
            const enrolar = showingEnrolarData ? row : getEnrolarRow(row);
            const persona = enrolar?.nombre_completo || row.nombre_persona || row.persona || '-';
            const correo = enrolar?.correo || row.correo || '-';
            const documento = enrolar?.documento_identidad || row.documento_identidad || '-';
            const tipoSangre = enrolar?.tipo_sangre || row.tipo_sangre || '-';
            const perfil = enrolar?.perfil || row.perfil || '-';
            const uid = enrolar?.tarjeta_uid || row.tarjeta_uid || row.uid_tarjeta || row.uid || '-';
            const pin = enrolar?.pin || row.tarjeta_pin || row.pin || '-';
            const estadoRaw = enrolar?.estado ?? row.estado ?? row.accion ?? row.tipo ?? row.estado_tarjeta ?? row.estado_actual ?? '-';
            const estado = formatEstado(estadoRaw);
            const accion = getAccionLabel(row);
            const isDeleted = normalizeActionValue(estadoRaw) === 'eliminado' || normalizeActionValue(accion) === 'eliminada';
            const rowClassName = isDeleted ? 'table-danger text-muted' : '';
            const responsable = row.responsable || row.ejecutado_por || 'Sistema';
            const fecha = row.fecha_hora || row.fecha_de_registro || enrolar?.fecha_de_registro || '-';
            return (
              <tr key={i} className={rowClassName}>
                <td>{row.id || '-'}</td>
                <td>{persona}</td>
                <td>{correo}</td>
                <td>{documento}</td>
                <td>{tipoSangre}</td>
                <td>{perfil}</td>
                <td>{uid}</td>
                <td>{pin}</td>
                <td>{renderEstadoBadge(estadoRaw)}</td>
                <td>{accion}</td>
                <td>{responsable}</td>
                <td>{fecha}</td>
              </tr>
            );
          }) : (
            <tr><td colSpan={12} className="text-center">Sin resultados</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
