import React from 'react';

export default function ModuloAdministracion({ onBack }) {
  return (
    <div className="container mt-4">
      <h2 className="mb-4">⚙️ Módulo de Administración Web</h2>
      <div className="text-start mb-3">
        <button className="btn btn-outline-secondary" onClick={onBack}>
          ← Volver al Panel de Administración
        </button>
      </div>
      <div className="list-group">
        <a href="/admin/personas" className="list-group-item list-group-item-action">
          👤 Registro de Personas
        </a>
        <a href="/admin/usuarios" className="list-group-item list-group-item-action">
          🔐 Gestión de Usuarios y Roles
        </a>
        <a href="/admin/auditoria" className="list-group-item list-group-item-action">
          📋 Auditoría de Cambios
        </a>
      </div>
    </div>
  );
}
