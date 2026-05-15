import React, { useState } from 'react';
import Personas from '../modulos/administracion/personas/Personas';
import TarjetasRegistradas from '../modulos/accesos/TarjetasRegistradas';
import AccesosHistorial from '../modulos/reportes/AccesosHistorial';
import TarjetasHistorial from '../modulos/reportes/TarjetasHistorial';

export default function AdminDashboard({ usuario, onLogout }) {
  const [view, setView] = useState('dashboard'); // 'dashboard' | 'personas' | 'tarjetas' | 'accesos_historial' | 'tarjetas_historial'

  let content = null;
  if (view === 'personas') content = <Personas />;
  else if (view === 'tarjetas') content = <TarjetasRegistradas />;
  else if (view === 'accesos_historial') content = <AccesosHistorial onVolver={() => setView('dashboard')} />;
  else if (view === 'tarjetas_historial') content = <TarjetasHistorial onVolver={() => setView('dashboard')} />;
  else
    content = (
      <div className="container mt-5">
        <h2 className="mb-4">Bienvenido, {usuario} 👋</h2>
        <div className="list-group">
          <button onClick={() => setView('personas')} className="list-group-item list-group-item-action">
            👤 Gestión de Personas
          </button>
          <button onClick={() => setView('tarjetas')} className="list-group-item list-group-item-action">
            🔐 Gestión de Tarjetas RFID
          </button>
          <button onClick={() => setView('accesos_historial')} className="list-group-item list-group-item-action">
            📊 Reporte de Historial de Accesos
          </button>
          <button onClick={() => setView('tarjetas_historial')} className="list-group-item list-group-item-action">
            💳 Historial de acciones en personas
          </button>
          <button onClick={onLogout} className="list-group-item list-group-item-action text-danger">
            🚪 Cerrar Sesión
          </button>
        </div>
      </div>
    );

  return <>{content}</>;
}
