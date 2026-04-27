import React from 'react';

export default function ModuloReportesTabla({ resultados = [], onVolver }) {
  const handleVolver = () => {
    if (typeof onVolver === 'function') return onVolver();
    window.history.back();
  };

  return (
    <div className="container mt-4">
      <div className="text-start mb-3">
        <button className="btn btn-outline-secondary" onClick={handleVolver} title="Regresar al panel de reportes">
          <span className="me-1">←</span> Volver al Módulo de Reportes
        </button>
      </div>
      <h2>Historial de Acciones sobre Tarjetas RFID</h2>
      <table className="table table-bordered table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Fecha</th>
            <th>Usuario</th>
            <th>ID Tarjeta</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          {resultados.length > 0 ? resultados.map((row, i) => (
            <tr key={i}>
              <td>{row.id}</td>
              <td>{row.fecha}</td>
              <td>{row.usuario_nombre}</td>
              <td>{row.id_tarjeta}</td>
              <td>{row.accion === 'alta' ? 'Alta' : 'Baja'}</td>
            </tr>
          )) : (
            <tr><td colSpan={5} className="text-center">Sin resultados</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
import React from 'react';

export default function ModuloReportesTabla({ resultados = [] }) {
  return (
    <div className="container mt-4">
      <h2>Historial de Acciones sobre Tarjetas RFID</h2>
      <table className="table table-bordered table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Fecha</th>
            <th>Usuario</th>
            <th>ID Tarjeta</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          {resultados.length > 0 ? resultados.map((row, i) => (
            <tr key={i}>
              <td>{row.id}</td>
              <td>{row.fecha}</td>
              <td>{row.usuario_nombre}</td>
              <td>{row.id_tarjeta}</td>
              <td>{row.accion === 'alta' ? 'Alta' : 'Baja'}</td>
            </tr>
          )) : (
            <tr><td colSpan={5} className="text-center">Sin resultados</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
