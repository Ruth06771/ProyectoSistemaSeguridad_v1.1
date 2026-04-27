import React, { useEffect, useState } from 'react';

export default function PerfilPersona({ onGoHome, onNavigate }) {
  const [personas, setPersonas] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchPersonas = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/personas', { credentials: 'include' });
      const data = await res.json();
      setPersonas(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error cargando personas', err);
      setPersonas([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPersonas(); }, []);

  const handleDelete = async id => {
    if (!window.confirm('¿Eliminar esta persona?')) return;
    try {
      await fetch(`/api/personas/${id}`, { method: 'DELETE', credentials: 'include' });
      fetchPersonas();
    } catch (err) {
      console.error(err);
      alert('Error al eliminar');
    }
  };

  const handleEditNavigate = (id) => {
    if (typeof window !== 'undefined' && window) {
      window.__editPersonaId = id;
    }
    if (typeof onNavigate === 'function') {
      onNavigate('personas');
    } else {
      window.location.href = `/admin/personas#edit-${id}`;
    }
  };

  const changeRole = async (id, rol) => {
    try {
      // Send minimal payload: only rol and keep current estado to avoid linking other data
      const persona = personas.find(p => p.id === id) || {};
      const payload = {
        rol,
        estado: (persona.estado === 0 || persona.estado === '0' || persona.estado === false) ? 0 : 1
      };
      const res = await fetch(`/api/personas/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
      });
      const j = await res.json();
      if (res.ok && j.success) {
        fetchPersonas();
      } else {
        alert(j.error || j.message || 'Error actualizando rol');
      }
    } catch (err) {
      console.error(err);
      alert('Error de red al actualizar rol');
    }
  };

  const toggleEstado = async (id, currentEstado) => {
    try {
      const persona = personas.find(p => p.id === id) || {};
      const payload = {
        // Only change estado; keep existing rol to avoid touching other fields
        rol: persona.rol || persona.role || 'estudiante',
        estado: (currentEstado === 0 || currentEstado === '0' || currentEstado === false) ? 1 : 0
      };

      const res = await fetch(`/api/personas/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
      });
      const j = await res.json();
      if (res.ok && j.success) {
        fetchPersonas();
      } else {
        alert(j.error || j.message || 'Error cambiando estado');
      }
    } catch (err) {
      console.error(err);
      alert('Error de red al cambiar estado');
    }
  };

  return (
    <div className="container py-4">
      <div className="card shadow-sm">
        <div className="card-header d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Perfil de Personas</h5>
          <div>
            <button className="btn btn-sm btn-secondary me-2" onClick={fetchPersonas}>Refrescar</button>
            <button className="btn btn-sm btn-outline-secondary" onClick={onGoHome}>Volver</button>
          </div>
        </div>
        <div className="card-body">
          {loading ? (
            <p>Cargando personas...</p>
          ) : (
            <div className="table-responsive">
              <table className="table table-sm table-hover">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Rol</th>
                    <th>Estado</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {personas.map(p => (
                    <tr key={p.id}>
                      <td>{p.id}</td>
                      <td className="text-capitalize">{p.rol || p.role || 'estudiante'}</td>
                      <td>
                        {/** Estado: treat 1/true/'1' as active */}
                        { (p.estado === 0 || p.estado === '0' || p.estado === false) ? (
                          <span className="badge bg-secondary">Inactivo</span>
                        ) : (
                          <span className="badge bg-success">Activo</span>
                        ) }
                      </td>
                      <td>
                        {/** Dropdown removed; only estado toggle and delete */}
                        <button className="btn btn-sm btn-warning me-2" type="button" onClick={() => toggleEstado(p.id, p.estado)}>Cambiar estado</button>
                        <button className="btn btn-sm btn-danger" type="button" onClick={() => handleDelete(p.id)}>Eliminar</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}