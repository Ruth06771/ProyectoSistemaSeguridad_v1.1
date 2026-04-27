import React from 'react';
import './sidebar.css';

export default function Sidebar({ collapsed, onToggle, onNavigate }) {
  return (
    <aside className={`app-sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
  <h4>Facultad de Tecnologia</h4>
        <button className="btn btn-sm btn-light" onClick={onToggle}>{collapsed ? '▶' : '◀'}</button>
      </div>
      <nav className="sidebar-nav">
        <div className="sidebar-section">
          <div className="sidebar-title">Configuración</div>
          <ul>
            <li onClick={() => onNavigate('personas')}>Registro de persona</li>
            <li onClick={() => onNavigate('registro_tarjeta')}>Registro de tarjeta</li>
            <li onClick={() => onNavigate('tipo_movimiento')}>Tipo de movimiento</li>
            <li onClick={() => onNavigate('tipo_registro')}>Tipo de registro</li>
            <li onClick={() => onNavigate('perfil_persona')}>Perfil de persona</li>
          </ul>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-title">Enrolar</div>
          <ul>
            <li onClick={() => onNavigate('enrolar')}>Enrolar</li>
          </ul>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-title">Seguridad</div>
          <ul>
            <li onClick={() => onNavigate('usuarios')}>Registrar usuario</li>
            <li onClick={() => onNavigate('permisos')}>Registrar permiso</li>
            <li onClick={() => onNavigate('roles')}>Registrar roles</li>
            <li onClick={() => onNavigate('bitacora')}>Bitácora</li>
          </ul>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-title">Reportes</div>
          <ul>
            <li onClick={() => onNavigate('reportes_ingresos')}>Ingresos de personas</li>
            <li onClick={() => onNavigate('tarjetas_historial')}>Historial tarjetas</li>
            <li onClick={() => onNavigate('accesos_historial')}>Historial accesos</li>
          </ul>
        </div>
      </nav>
    </aside>
  );
}
import React from 'react';

// Sidebar intentionally disabled: the app uses the TopNav (navigation on top).
// If in future you want the sidebar again, restore the original component here.
export default function Sidebar() {
  return null;
}
