import React, { useState, useEffect } from 'react';

export default function Usuarios({ onGoHome }) {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchUsuarios = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/usuarios', { credentials: 'include' });
      const data = await res.json();
      setUsuarios(Array.isArray(data) ? data : []);
    } catch (err) {
      setUsuarios([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchUsuarios(); }, []);

  const changeRole = async (id, rol) => {
    try {
      const res = await fetch(`/api/usuarios/${id}/rol`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ rol })
      });
      const data = await res.json();
      if (data.success) fetchUsuarios(); else alert(data.error || 'Error al actualizar rol');
    } catch (err) {
      alert('Error de red al actualizar rol');
    }
  };

  return (
    <div className="container py-4">
      <div className="card shadow-sm">
        <div className="card-header d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Gestión de Usuarios / Roles</h5>
          <div>
            <button className="btn btn-sm btn-secondary me-2" onClick={fetchUsuarios}>Refrescar</button>
            <button className="btn btn-sm btn-outline-secondary" onClick={onGoHome}>Volver</button>
          </div>
        </div>
        <div className="card-body">
          {loading ? (<p>Cargando usuarios...</p>) : (
            <div className="table-responsive">
              <table className="table table-sm">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Correo</th>
                    <th>Rol</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {usuarios.map(u => (
                    <tr key={u.id}>
                      <td>{u.id}</td>
                      <td>{u.nombre_completo}</td>
                      <td>{u.correo}</td>
                      <td className="text-capitalize">{u.rol || 'estudiante'}</td>
                      <td>
                        <select className="form-select form-select-sm d-inline-block w-auto me-2" defaultValue={u.rol || 'estudiante'} onChange={(e) => changeRole(u.id, e.target.value)}>
                          <option value="administrador">Administrador</option>
                          <option value="docente">Docente</option>
                          <option value="estudiante">Estudiante</option>
                          <option value="auxiliar">Auxiliar</option>
                          <option value="invitado">Invitado</option>
                        </select>
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
