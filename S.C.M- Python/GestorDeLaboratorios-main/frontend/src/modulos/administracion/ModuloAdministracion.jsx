import React from 'react';

export default function ModuloAdministracion({ onBack, onNavigate }) {
  return (
    <div className="container mt-4">
      <h2 className="mb-4">⚙️ Módulo de Administración Web</h2>
      <div className="text-start mb-3">
        <button className="btn btn-outline-secondary" onClick={onBack}>
          ← Volver al Panel de Administración
        </button>
      </div>
      <div className="list-group">
        <button type="button" className="list-group-item list-group-item-action text-start" onClick={() => onNavigate ? onNavigate('personas') : window.location.href = '/admin/personas'}>
          👤 Registro de Personas
        </button>
        <button type="button" className="list-group-item list-group-item-action text-start" onClick={() => onNavigate ? onNavigate('usuarios') : window.location.href = '/admin/usuarios'}>
          🔐 Gestión de Usuarios y Roles
        </button>
        <button type="button" className="list-group-item list-group-item-action text-start" onClick={() => onNavigate ? onNavigate('dispositivos') : window.location.href = '/admin/dispositivos'}>
          📡 Gestión de Dispositivos (ESP)
        </button>
        <button type="button" className="list-group-item list-group-item-action text-start" onClick={() => onNavigate ? onNavigate('tarjetas_historial') : window.location.href = '/admin/auditoria'}>
          🗂️ Auditoría de Cambios
        </button>
      </div>
    </div>
  );
}
