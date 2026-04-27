import React, { useState, useEffect } from 'react';

export default function TipoMovimiento({ onGoHome }) {
  const [movimientos, setMovimientos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editId, setEditId] = useState(null);
  const [editNombre, setEditNombre] = useState('');
  const [msg, setMsg] = useState('');

  const fetchMovimientos = () => {
    setLoading(true);
    fetch('/api/tipo_movimiento', { credentials: 'include' })
      .then(res => res.json())
      .then(data => setMovimientos(data || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchMovimientos();
  }, []);

  const handleEdit = (mov) => {
    setEditId(mov.id);
    setEditNombre(mov.nombre);
  };

  const saveEdit = async () => {
    if (!editNombre || editNombre.trim() === '') { setMsg('El nombre es obligatorio'); return; }
    setMsg('Guardando...');
    try {
      const mov = movimientos.find(m => m.id === editId);
      const res = await fetch(`/api/tipo_movimiento/${editId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre: editNombre, estado: mov.estado }),
        credentials: 'include'
      });
      const j = await res.json();
      if (res.ok) {
        setMsg('✓ Actualizado');
        fetchMovimientos();
        setEditId(null);
        setEditNombre('');
        setTimeout(() => setMsg(''), 2000);
      } else {
        setMsg(j.error || 'Error al guardar');
      }
    } catch (e) { setMsg('Error de red'); }
  };

  const toggleEstado = async (mov) => {
    const nuevoEstado = mov.estado === 1 ? 0 : 1;
    try {
      const res = await fetch(`/api/tipo_movimiento/${mov.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre: mov.nombre, estado: nuevoEstado }),
        credentials: 'include'
      });
      if (res.ok) {
        fetchMovimientos();
      }
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Seguro que deseas eliminar? Esta acción no se puede deshacer.')) return;
    try {
      const res = await fetch(`/api/tipo_movimiento/${id}`, { method: 'DELETE', credentials: 'include' });
      if (res.ok) {
        fetchMovimientos();
        setMsg('Eliminado');
        setTimeout(() => setMsg(''), 2000);
      } else {
        setMsg('Error al eliminar');
      }
    } catch (e) { setMsg('Error de red'); }
  };

  const getEstadoText = (estado) => estado === 1 ? 'Activo' : 'Inactivo';
  const getEstadoBadgeClass = (estado) => estado === 1 ? 'bg-success' : 'bg-secondary';

  return (
    <div className="container py-4">
      <button className="btn btn-outline-secondary mb-3" onClick={() => window.location.href = '/'}>
        ← Volver al inicio
      </button>

      <div className="card">
        <div className="card-header d-flex justify-content-between align-items-center">
          <span>Tipos de Movimiento</span>
          <span className="badge bg-info">{movimientos.length}</span>
        </div>
        <div className="card-body p-0">
          {loading ? (
            <div className="text-center py-5"><span className="spinner-border text-primary" role="status"></span></div>
          ) : movimientos.length === 0 ? (
            <div className="text-center text-muted py-5">Sin tipos de movimiento</div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0">
                <thead className="table-light">
                  <tr>
                    <th style={{ width: '50px' }}>ID</th>
                    <th>Nombre</th>
                    <th style={{ width: '120px' }}>Estado</th>
                    <th style={{ width: '150px' }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {movimientos.map(mov => (
                    <tr key={mov.id}>
                      <td className="text-muted"><small>#{mov.id}</small></td>
                      <td>
                        {editId === mov.id ? (
                          <input
                            type="text"
                            className="form-control form-control-sm"
                            value={editNombre}
                            onChange={e => setEditNombre(e.target.value)}
                            autoFocus
                          />
                        ) : (
                          mov.nombre
                        )}
                      </td>
                      <td><span className={`badge ${getEstadoBadgeClass(mov.estado)}`}>{getEstadoText(mov.estado)}</span></td>
                      <td>
                        {editId === mov.id ? (
                          <>
                            <button
                              className="btn btn-sm btn-success me-2"
                              onClick={saveEdit}
                              title="Guardar"
                            >
                              <i className="bi bi-check"></i>
                            </button>
                            <button
                              className="btn btn-sm btn-outline-secondary"
                              onClick={() => { setEditId(null); setEditNombre(''); }}
                              title="Cancelar"
                            >
                              <i className="bi bi-x"></i>
                            </button>
                          </>
                        ) : (
                          <>
                            <button
                              className="btn btn-sm btn-outline-info me-2"
                              title={mov.estado === 1 ? 'Desactivar' : 'Activar'}
                              onClick={() => toggleEstado(mov)}
                            >
                              <i className={`bi ${mov.estado === 1 ? 'bi-toggle-on' : 'bi-toggle-off'}`}></i>
                            </button>
                            <button className="btn btn-sm btn-warning me-2" title="Editar" onClick={() => handleEdit(mov)}>
                              <i className="bi bi-pencil-square"></i>
                            </button>
                            <button className="btn btn-sm btn-danger" title="Eliminar" onClick={() => handleDelete(mov.id)}>
                              <i className="bi bi-trash"></i>
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {msg && (
        <div className={`alert ${msg.includes('✓') ? 'alert-success' : msg.includes('Error') ? 'alert-danger' : 'alert-info'} mt-3`}>
          {msg}
        </div>
      )}
    </div>
  );
}
