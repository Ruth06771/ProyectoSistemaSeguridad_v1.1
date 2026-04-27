import React from 'react';

export default function ModuloReportes({ onVolver }) {
  return (
    <div className="container mt-4">
      <h2 className="mb-4">📊 Módulo de Reportes</h2>
      <div className="text-start mb-3">
        <button className="btn btn-outline-secondary" onClick={onVolver} title="Regresar al panel de administrador">
          <span className="me-2">←</span> Volver al panel de administrador
        </button>
      </div>
      <div className="list-group">
        <a href="/modulos/reportes/accesos_historial" className="list-group-item list-group-item-action">
          🔐 Reporte de Historial de Accesos
        </a>
        <a href="/modulos/reportes/tarjetas_historial" className="list-group-item list-group-item-action">
          💳 Reporte de Altas y Bajas de Tarjetas RFID
        </a>
        <a href="#" className="list-group-item list-group-item-action disabled">
          📦 Reporte de Movimientos de Inventario (próximamente)
        </a>
        <a href="#" className="list-group-item list-group-item-action disabled">
          ⚙️ Reporte de Actividades en Administración Web (próximamente)
        </a>
        <a href="/modulos/reportes/accesos_personal" className="list-group-item list-group-item-action">
          🗾 Reporte de Accesos Detallado por Usuario
        </a>
      </div>
    </div>
  );
}
