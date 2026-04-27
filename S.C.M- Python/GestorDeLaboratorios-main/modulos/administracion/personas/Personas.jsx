import React, { useState, useEffect } from 'react';
import RegistrarPersona from './RegistrarPersona';
import EditarPersona from './EditarPersona';

export default function Personas() {
  const [personas, setPersonas] = useState([]);
  const [view, setView] = useState('list'); // 'list' | 'add' | 'edit'
  const [editId, setEditId] = useState(null);

  // Cargar personas
  const fetchPersonas = () => {
    fetch('/api/personas', { credentials: 'include' })
      .then(res => res.json())
      .then(setPersonas);
  };

  useEffect(() => {
    if (view === 'list') fetchPersonas();
  }, [view]);

  // Navegación
  const handleAdd = () => setView('add');
  const handleEdit = (id) => { setEditId(id); setView('edit'); };
  const handleBack = () => setView('list');

  if (view === 'add') {
    return <RegistrarPersona onSuccess={handleBack} onCancel={handleBack} />;
  }
  if (view === 'edit') {
    return <EditarPersona id={editId} onSubmit={handleBack} onCancel={handleBack} />;
  }

  return (
    <div className="container py-4">
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
          <div className="table-responsive">
            <table className="table table-striped table-hover align-middle mb-0">
              <thead className="table-dark">
                <tr>
                  <th>ID</th>
                  <th>Nombre Completo</th>
                  <th>Correo</th>
                  <th>Documento</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {personas.length > 0 ? personas.map(p => (
                  <tr key={p.id}>
                    <td>{p.id}</td>
                    <td>{p.nombre_completo}</td>
                    <td>{p.correo}</td>
                    <td><span className="badge bg-secondary">{p.documento_identidad}</span></td>
                    <td>
                      <button className="btn btn-sm btn-warning me-2" title="Editar" onClick={() => handleEdit(p.id)}>
                        <i className="bi bi-pencil-square"></i>
                      </button>
                      {/* Aquí puedes agregar botón de eliminar si lo deseas */}
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={5} className="text-center text-muted py-4">
                      Sin personas registradas
                    </td>
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
