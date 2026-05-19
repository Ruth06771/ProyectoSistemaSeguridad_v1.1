import React, { useState, useEffect } from 'react';

export default function ReportesIngresos({ onFiltrar, resultados = [], filtros = {}, onExportExcel, onExportPDF, onVolver }) {
  const [form, setForm] = useState(filtros);
  const [tarjetasRegistradas, setTarjetasRegistradas] = useState([]);
  const [tarjetasByUid, setTarjetasByUid] = useState({});

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

  const normalizeAccionLabel = (accion) => {
    const value = String(accion || '').trim().toLowerCase();
    if (value === 'creada' || value === 'alta') return 'Alta';
    if (value === 'baja') return 'Baja';
    if (value === 'editada' || value === 'edicion' || value === 'modificada') return 'Editada';
    if (value === 'eliminada') return 'Eliminada';
    return accion || '-';
  };

  const normalizeUid = (row) => {
    return row.uid_tarjeta || row.uid || row.tarjeta || row.tarjeta_uid || '';
  };

  const normalizeResponsable = (row) => {
    return row.responsable || row.ejecutado_por || row.usuario || 'Sistema';
  };

  useEffect(() => {
    const fetchTarjetasRegistradas = async () => {
      try {
        const response = await fetch('/api/tarjetas', { credentials: 'include' });
        const data = await response.json();
        const lista = Array.isArray(data) ? data : (data && data.value ? data.value : []);
        setTarjetasRegistradas(lista);
        const byUid = lista.reduce((acc, tarjeta) => {
          const uid = tarjeta.uid || tarjeta.codigo || tarjeta.tarjeta_uid;
          if (uid) acc[uid] = tarjeta;
          return acc;
        }, {});
        setTarjetasByUid(byUid);
      } catch (err) {
        setTarjetasRegistradas([]);
        setTarjetasByUid({});
      }
    };

    fetchTarjetasRegistradas();
    // Cargar datos iniciales al montar el componente
    if (onFiltrar) onFiltrar(form || {});
  }, []);

  // Auto-refresh cada 10 segundos para detectar cambios en tarjetas
  useEffect(() => {
    const interval = setInterval(() => {
      if (onFiltrar) onFiltrar(form || {});
    }, 10000);
    return () => clearInterval(interval);
  }, [form, onFiltrar]);

  return (
    <div className="container mt-4">
      <h2>📇 Historial de Registro de Tarjetas</h2>
      <div className="text-start mb-3">
        <button
          className="btn btn-outline-secondary"
          onClick={onVolver}
          title="Regresar al panel de informes"
        >
          <span className="me-1">←</span> Volver al Módulo de Reportes
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
            <option value="editada">Editada</option>
            <option value="eliminada">Eliminada</option>
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

        <div className="col-12 d-flex gap-2 flex-wrap">
          <button className="btn btn-primary" type="submit">🔍 Filtrar</button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => {
              setForm({});
              if (onFiltrar) onFiltrar({});
            }}
          >
            🔃 Refresh
          </button>
          <button
            type="button"
            className="btn btn-success"
            onClick={() => {
              if (onExportExcel) {
                onExportExcel(form);
                return;
              }
              const params = new URLSearchParams(form).toString();
              openDownload(`/exportar_excel_tarjetas?${params}`);
            }}
          >
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
            <th>UID Tarjeta</th>
            <th>Acción</th>
            <th>Responsable</th>
            <th>Fecha y Hora</th>
          </tr>
        </thead>
        <tbody>
          {resultados.length > 0 ? (
            resultados.map((row, i) => {
              const uid = normalizeUid(row);
              const accionLabel = normalizeAccionLabel(row.accion); 
              return (
                <tr key={i}>
                  <td>{row.id || '-'}</td>
                  <td>{uid || '-'}</td>
                  <td>{accionLabel}</td>
                  <td>{normalizeResponsable(row)}</td>
                  <td>{row.fecha_hora || row.fecha_de_registro || '-'}</td>
                </tr>
              );
            })
          ) : (
            <tr>
              <td colSpan={5} className="text-center">
                Sin resultados
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

