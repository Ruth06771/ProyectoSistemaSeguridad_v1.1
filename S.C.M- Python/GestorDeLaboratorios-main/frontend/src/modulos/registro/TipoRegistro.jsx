import React, { useState, useEffect } from 'react';

export default function TipoRegistro({ onGoHome }) {
  const [registros, setRegistros] = useState([]);

  useEffect(() => {
    // Cargar tipos de registro hardcodeados
    setRegistros([
      { id: 1, nombre: 'Pin', perfil_fk: 1, estado: 1 },
      { id: 2, nombre: 'Tarjeta', perfil_fk: 1, estado: 1 }
    ]);
  }, []);

  function toggleRegistroEstado(item) {
    const newEstado = item.estado === 1 || item.estado === '1' ? 0 : 1;
    // Optimistic update
    setRegistros(prev => prev.map(d => (d.id === item.id ? { ...d, estado: newEstado } : d)));
    fetch(`/api/tipo_registro/${item.id}`, {
      method: 'PUT',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre: item.nombre, perfil_fk: item.perfil_fk, estado: newEstado })
    }).then(res => {
      if (!res.ok) {
        setRegistros(prev => prev.map(d => (d.id === item.id ? { ...d, estado: item.estado } : d)));
      }
    }).catch(() => {
      setRegistros(prev => prev.map(d => (d.id === item.id ? { ...d, estado: item.estado } : d)));
    });
  }

  function eliminarRegistro(id) {
    if (!window.confirm('¿Eliminar este tipo de registro?')) return;
    fetch(`/api/tipo_registro/${id}`, { method: 'DELETE', credentials: 'include' })
      .then(res => res.json())
      .then(() => setRegistros(prev => prev.filter(d => d.id !== id)))
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
              <th>Perfil (FK)</th>
              <th>Estado</th>
              <th style={{ width: '160px' }}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {registros.map(d => (
              <tr key={d.id}>
                <td>{d.id}</td>
                <td>{d.nombre}</td>
                <td>{d.perfil_fk}</td>
                <td>{d.estado === 1 || d.estado === '1' ? 'Activo' : 'Inactivo'}</td>
                <td>
                  <button className="btn btn-sm btn-outline-primary me-2" onClick={() => toggleRegistroEstado(d)}>
                    Toggle
                  </button>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => eliminarRegistro(d.id)}>
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
            {registros.length === 0 && (
              <tr>
                <td colSpan={5} className="text-center text-muted">No hay tipos de registro registrados.</td>
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

