import React, { useState, useEffect } from 'react';
import RegistrarPersona from './RegistrarPersona';
import EditarPersona from './EditarPersona';

export default function Personas({ onGoHome }) {
  const [personas, setPersonas] = useState([]);
  const [view, setView] = useState('list'); // 'list' | 'add' | 'edit'
  const [editId, setEditId] = useState(null);
  const [editPersona, setEditPersona] = useState(null);
  const [deleteMsg, setDeleteMsg] = useState('');

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
        setDeleteMsg('Persona eliminada correctamente');
        fetchPersonas();
      } else {
        setDeleteMsg(data.error || 'Error al eliminar');
      }
    } catch (err) {
      setDeleteMsg('Error de red');
    }
    setTimeout(() => setDeleteMsg(''), 2500);
  };

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
          <div className="d-flex justify-content-end p-3">
            <button className="btn btn-primary" onClick={handleAdd}>
              <i className="bi bi-person-plus me-2"></i> Nueva Persona
            </button>
          </div>

          {deleteMsg && (
            <div className="p-3">
              <div className="alert alert-info" role="alert">{deleteMsg}</div>
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
                        <button className="btn btn-sm btn-warning me-2" title="Editar" onClick={() => handleEdit(p.id)}>
                          <i className="bi bi-pencil-square"></i>
                        </button>
                        <button className="btn btn-sm btn-danger" title="Eliminar" onClick={() => handleDelete(p.id)}>
                          <i className="bi bi-trash"></i>
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="text-center text-muted py-4">Sin personas registradas</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}