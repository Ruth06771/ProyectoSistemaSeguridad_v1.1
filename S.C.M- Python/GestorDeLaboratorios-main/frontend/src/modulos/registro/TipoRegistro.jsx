import React, { useState, useEffect } from 'react';

export default function TipoRegistro({ onGoHome }) {
  const [dispositivos, setDispositivos] = useState([]);

  useEffect(() => {
    // Cargar tipos de dispositivo (solo columnas id, nombre, estado)
    fetch('/api/tipo_dispositivo', { credentials: 'include' })
      .then(res => {
        if (!res.ok) throw new Error('Error al cargar tipos de dispositivo');
        return res.json();
      })
      .then(data => setDispositivos(data || []))
      .catch(err => console.error(err));
  }, []);

  function toggleDispositivoEstado(item) {
    const newEstado = item.estado === 1 || item.estado === '1' ? 0 : 1;
    // Optimistic update
    setDispositivos(prev => prev.map(d => (d.id === item.id ? { ...d, estado: newEstado } : d)));
    fetch(`/api/tipo_dispositivo/${item.id}`, {
      method: 'PUT',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre: item.nombre, estado: newEstado })
    }).then(res => {
      if (!res.ok) {
        setDispositivos(prev => prev.map(d => (d.id === item.id ? { ...d, estado: item.estado } : d)));
      }
    }).catch(() => {
      setDispositivos(prev => prev.map(d => (d.id === item.id ? { ...d, estado: item.estado } : d)));
    });
  }

  function eliminarDispositivo(id) {
    if (!window.confirm('¿Eliminar este tipo de dispositivo?')) return;
    fetch(`/api/tipo_dispositivo/${id}`, { method: 'DELETE', credentials: 'include' })
      .then(res => res.json())
      .then(() => setDispositivos(prev => prev.filter(d => d.id !== id)))
      .catch(err => console.error(err));
  }

  return (
    <div className="card">
      <div className="card-header">TIPO DE REGISTRO</div>
      <div className="card-body">
        
        <table className="table table-bordered table-sm">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Estado</th>
              <th style={{ width: '160px' }}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {dispositivos.map(d => (
              <tr key={d.id}>
                <td>{d.id}</td>
                <td>{d.nombre}</td>
                <td>{d.estado === 1 || d.estado === '1' ? 'Activo' : 'Inactivo'}</td>
                <td>
                  <button className="btn btn-sm btn-outline-primary me-2" onClick={() => toggleDispositivoEstado(d)}>
                    Toggle
                  </button>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => eliminarDispositivo(d.id)}>
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
            {dispositivos.length === 0 && (
              <tr>
                <td colSpan={4} className="text-center text-muted">No hay tipos de dispositivo registrados.</td>
              </tr>
            )}
          </tbody>
        </table>

        <div className="mt-3">
          <button className="btn btn-secondary" onClick={onGoHome}>
            Volver al inicio
          </button>
        </div>
      </div>
    </div>
  );
}

