import React, { useState, useEffect } from 'react';
import RegistrarPersona from './RegistrarPersona';
import EditarPersona from './EditarPersona';
import PermissionGate from '../../../ui/PermissionGate';

export default function Personas({ onGoHome }) {
  const [personas, setPersonas] = useState([]);
  const [view, setView] = useState('list'); // 'list' | 'add' | 'edit'
  const [editId, setEditId] = useState(null);
  const [editPersona, setEditPersona] = useState(null);
  const [statusMsg, setStatusMsg] = useState('');

  // Cargar personas
  const fetchPersonas = () => {
    fetch('/api/personas', { credentials: 'include' })
      .then(res => res.json())
      .then(setPersonas)
      .catch(() => setPersonas([]));
  };

  useEffect(() => {
    if (view === 'list') fetchPersonas();
  }, [view]);

  // If another module set a global edit id (SPA navigation), open editor for that id
  useEffect(() => {
    try {
      if (typeof window !== 'undefined' && window.__editPersonaId) {
        const id = window.__editPersonaId;
        window.__editPersonaId = null;
        if (id) handleEdit(id);
      }
    } catch (e) {
      // ignore
    }
  }, []);

  // Navegación
  const handleAdd = () => setView('add');
  const handleEdit = async (id) => {
    setEditId(id);
    // fetch persona details to pass to EditarPersona
    try {
      const res = await fetch(`/api/personas/${id}`, { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        setEditPersona(data);
      } else {
        setEditPersona(null);
      }
    } catch (err) {
      console.error('Error fetching persona', err);
      setEditPersona(null);
    }
    setView('edit');
  };
  const handleBack = () => setView('list');

  // Eliminar persona
  const handleDelete = async (id) => {
    if (!window.confirm('¿Seguro que deseas eliminar esta persona?')) return;
    try {
      const res = await fetch(`/api/personas/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      const data = await res.json();
      if (data.success) {
        setStatusMsg('Persona eliminada correctamente');
        setPersonas(prev => prev.filter(p => p.id !== id));
      } else {
        setStatusMsg(data.error || 'Error al eliminar');
      }
    } catch (err) {
      setStatusMsg('Error de red');
    }
    setTimeout(() => setStatusMsg(''), 2500);
  };

  // Actualizar estado de la persona a Activo/Inactivo
  const handleToggleEstado = async (id, estado) => {
    try {
      const res = await fetch(`/api/personas/${id}/estado`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ estado }),
      });
      const data = await res.json();
      if (data.success) {
        setStatusMsg(`Estado actualizado a ${estado === 1 ? 'Activo' : 'Inactivo'}`);
        if (estado === 0) {
          // Si se marca como inactivo (estado = 0), remover de la lista local
          setPersonas(prev => prev.filter(p => p.id !== id));
        } else {
          // Si se activa, actualizar el registro localmente
          setPersonas(prev => prev.map(p => p.id === id ? { ...p, estado } : p));
        }
      } else {
        setStatusMsg(data.error || 'Error al actualizar estado');
      }
    } catch (err) {
      console.error('Error updating estado:', err);
      setStatusMsg('Error de conexión. Verifica tu red e intenta nuevamente.');
    }
    setTimeout(() => setStatusMsg(''), 2500);
  };

  const handleRefresh = () => fetchPersonas();

  if (view === 'add') {
    return <RegistrarPersona onSuccess={handleBack} onCancel={handleBack} onGoHome={onGoHome} />;
  }
  if (view === 'edit') {
    return (
      <EditarPersona
        persona={editPersona}
        onSubmit={async (form) => {
          // perform PUT to update existing persona
          try {
            const res = await fetch(`/api/personas/${editId}`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              credentials: 'include',
              body: JSON.stringify(form),
            });
            const data = await res.json();
            if (data && data.success) {
              handleBack();
            } else {
              // still go back and refresh list (EditarPersona may show messages if implemented)
              handleBack();
            }
          } catch (err) {
            console.error('Error updating persona', err);
            handleBack();
          }
        }}
        onCancel={handleBack}
        onGoHome={onGoHome}
      />
    );
  }

  return (
    <PermissionGate permissionKey="administracion.ver" fallback={
      <div className="container py-4">
        <div className="alert alert-warning">Tu rol no tiene permisos para ver la gestión de personas.</div>
      </div>
    }>
      <div className="container py-4">
        
        <button className="btn btn-outline-secondary mb-3" onClick={() => window.location.href = '/'}>
           ← Volver al inicio
        </button>
      <div className="card shadow-sm mb-4">
        <div className="card-header bg-primary text-white d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Personas Registradas</h5>
          <span className="badge bg-info">{personas.length} personas</span>
        </div>
        <div className="card-body p-0">
          <div className="d-flex justify-content-end gap-2 p-3">
            <button className="btn btn-outline-secondary" onClick={handleRefresh}>
              <i className="bi bi-arrow-clockwise me-2"></i> Actualizar
            </button>
            <PermissionGate permissionKey="administracion.crear">
              <button className="btn btn-primary" onClick={handleAdd}>
                <i className="bi bi-person-plus me-2"></i> Nueva Persona
              </button>
            </PermissionGate>
          </div>

          {statusMsg && (
            <div className="p-3">
              <div className="alert alert-info" role="alert">{statusMsg}</div>
            </div>
          )}

          <div className="table-responsive">
            <table className="table table-striped table-hover align-middle mb-0">
              <thead className="table-dark">
                <tr>
                  <th>ID</th>
                  <th>Nombre Completo</th>
                  <th>Rol</th>
                  <th>Correo</th>
                  <th>Documento</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {personas && personas.length > 0 ? (
                  personas.map((p) => (
                    <tr key={p.id}>
                      <td>{p.id}</td>
                      <td>{p.nombre_completo}</td>
                      <td><span className="badge bg-secondary text-capitalize">{p.rol || 'estudiante'}</span></td>
                      <td>{p.correo}</td>
                      <td><span className="badge bg-secondary">{p.documento_identidad}</span></td>
                      <td>
                        <span className={`badge ${p.estado == 1 ? 'bg-success' : 'bg-secondary'}`}>
                          {p.estado == 1 ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td>
                        <div className="d-flex gap-1 flex-wrap">
                          <PermissionGate permissionKey="administracion.editar">
                            <button
                              type="button"
                              className={`btn btn-sm flex-fill ${p.estado == 1 ? 'btn-success' : 'btn-outline-success'}`}
                              onClick={() => handleToggleEstado(p.id, 1)}
                            >
                              Activo
                            </button>
                            <button
                              type="button"
                              className={`btn btn-sm flex-fill ${p.estado == 0 ? 'btn-danger' : 'btn-outline-danger'}`}
                              onClick={() => handleToggleEstado(p.id, 0)}
                            >
                              Inactivo
                            </button>
                            <button
                              type="button"
                              className="btn btn-sm btn-outline-warning flex-fill"
                              onClick={() => handleEdit(p.id)}
                            >
                              Editar
                            </button>
                          </PermissionGate>
                          <PermissionGate permissionKey="administracion.eliminar">
                            <button
                              type="button"
                              className="btn btn-sm btn-outline-danger flex-fill"
                              onClick={() => handleDelete(p.id)}
                            >
                              Eliminar
                            </button>
                          </PermissionGate>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} className="text-center text-muted py-4">Sin personas registradas</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    </PermissionGate>
  );
}