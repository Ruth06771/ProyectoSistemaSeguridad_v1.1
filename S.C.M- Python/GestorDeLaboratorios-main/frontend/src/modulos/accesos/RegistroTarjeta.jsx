import React, { useState, useEffect } from 'react';

export default function RegistroTarjeta({ onGoHome }) {
  const [form, setForm] = useState({ uid: '', pin: '', estado: 1 });
  const [editId, setEditId] = useState(null);
  const [msg, setMsg] = useState('');
  const [tarjetas, setTarjetas] = useState([]);
  const [loading, setLoading] = useState(false);

  const normalizeTarjeta = (tarjeta) => {
    const estado = tarjeta?.estado != null
      ? Number(tarjeta.estado)
      : tarjeta?.activo != null
        ? (tarjeta.activo === false ? 0 : 1)
        : 1;
    return {
      ...tarjeta,
      estado,
      activo: estado
    };
  };

  useEffect(() => {
    fetchTarjetas();
  }, []);

  const fetchTarjetas = () => {
    setLoading(true);
    fetch('/api/tarjetas', { credentials: 'include' })
      .then(r => r.json())
      .then(data => setTarjetas(Array.isArray(data) ? data.map(normalizeTarjeta) : []))
      .catch(() => setTarjetas([]))
      .finally(() => setLoading(false));
  };

  const resetForm = () => {
    setForm({ uid: '', pin: '', estado: 1 });
    setEditId(null);
    setMsg('');
  };

  const validateForm = () => {
    if (!form.uid || form.uid.trim() === '') return 'UID es obligatorio';
    if (!/^\d{8}$/.test((form.pin || '').toString().trim())) return 'El PIN debe tener exactamente 8 dígitos';
    return null;
  };

  const submit = async () => {
    const validationError = validateForm();
    if (validationError) { setMsg(validationError); return; }

    setMsg(editId ? 'Actualizando tarjeta...' : 'Guardando tarjeta...');
    try {
      const url = editId ? `/api/tarjetas/${editId}` : '/api/tarjetas';
      const payload = editId ? form : { uid: form.uid, pin: form.pin };
      const res = await fetch(url, {
        method: editId ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        credentials: 'include'
      });
      const data = await res.json();
      if (res.ok) {
        setMsg(editId ? '✓ Tarjeta actualizada correctamente' : '✓ Tarjeta registrada exitosamente');
        fetchTarjetas();
        resetForm();
        setTimeout(() => setMsg(''), 3000);
      } else {
        setMsg(data.message || data.error || 'Error al guardar');
      }
    } catch (e) {
      setMsg('Error de red');
    }
  };

  const cambiarEstado = async (id, nuevoEstado) => {
    const accion = nuevoEstado ? 'dar de alta' : 'dar de baja';
    if (!window.confirm(`¿Estás seguro de que deseas ${accion} esta tarjeta?`)) return;
    try {
      const res = await fetch(`/api/tarjetas/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ activo: nuevoEstado }),
        credentials: 'include'
      });
      const data = await res.json();
      if (res.ok) {
        setTarjetas(prev => prev.map(t => t.id === id ? normalizeTarjeta({ ...t, estado: nuevoEstado, activo: nuevoEstado }) : t));
        setMsg(`✓ Tarjeta ${nuevoEstado ? 'activada' : 'desactivada'} correctamente`);
        setTimeout(() => setMsg(''), 3000);
      } else {
        setMsg(data.message || data.error || 'Error al cambiar estado');
      }
    } catch (e) {
      setMsg('Error de red al cambiar estado');
    }
  };

  const iniciarEdicion = (tarjeta) => {
    setEditId(tarjeta.id);
    setForm({
      uid: tarjeta.uid || '',
      pin: tarjeta.pin || '',
      estado: tarjeta.estado != null ? tarjeta.estado : (tarjeta.activo !== false ? 1 : 0)
    });
    setMsg(`Editando tarjeta #${tarjeta.id}`);
  };

  const cancelarEdicion = () => {
    resetForm();
  };

  const eliminarTarjeta = async (id) => {
    if (!window.confirm('¿Estás seguro de eliminar esta tarjeta?')) return;
    try {
      const res = await fetch(`/api/tarjetas/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (res.ok) {
        setMsg('✓ Tarjeta eliminada correctamente');
        fetchTarjetas();
        if (editId === id) resetForm();
        setTimeout(() => setMsg(''), 3000);
      } else {
        const data = await res.json();
        setMsg(data.message || data.error || 'Error al eliminar');
      }
    } catch (e) {
      setMsg('Error de red al eliminar');
    }
  };

  return (
    <div className="container py-4">
      <button className="btn btn-outline-secondary mb-3" onClick={() => window.location.href = '/'}>
        ← Volver al inicio
      </button>

      <div className="row g-4">
        {/* Formulario */}
        <div className="col-lg-4">
          <div className="card mb-3 shadow-sm">
            <div className="card-header bg-white fw-bold">
              {editId ? `Editar Tarjeta #${editId}` : 'Registro de Tarjeta'}
            </div>
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label">UID <span className="text-danger">*</span></label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Ej: A1B2C3D4"
                  value={form.uid}
                  onChange={e => setForm({ ...form, uid: e.target.value })}
                />
              </div>
              <div className="mb-4">
                <label className="form-label">PIN <span className="text-danger">*</span></label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Ej: 12345678"
                  value={form.pin}
                  onChange={e => setForm({ ...form, pin: e.target.value })}
                  maxLength="8"
                />
                <small className="text-muted">Exactamente 8 dígitos numéricos</small>
              </div>
              <button className="btn btn-primary w-100" onClick={submit}>
                {editId ? 'Actualizar Tarjeta' : 'Guardar Tarjeta'}
              </button>
              {editId && (
                <button className="btn btn-outline-secondary w-100 mt-2" onClick={cancelarEdicion}>
                  Cancelar edición
                </button>
              )}
              {msg && <div className={`alert ${msg.includes('✓') ? 'alert-success' : 'alert-danger'} mt-3 mb-0`}><small>{msg}</small></div>}
            </div>
          </div>
        </div>

        {/* Tabla con los 4 botones */}
        <div className="col-lg-8">
          <div className="card shadow-sm">
            <div className="card-header bg-white fw-bold">Tarjetas Registradas</div>
            <div className="card-body p-0">
              {loading ? (
                <div className="text-center py-5"><span className="spinner-border text-primary"></span></div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover align-middle mb-0">
                    <thead className="table-light">
                      <tr>
                        <th style={{ width: '60px' }}>ID</th>
                        <th>UID</th>
                        <th>Estado</th>
                        <th className="text-center">Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tarjetas.slice(-10).map(t => (
                        <tr key={t.id}>
                          <td className="text-muted"><small>#{t.id}</small></td>
                          <td><code>{t.uid}</code></td>
                          <td>
                            {(() => {
                              const tarjetaEstado = t.estado != null ? Number(t.estado) : (t.activo !== false ? 1 : 0);
                              return (
                                <span className={`badge rounded-pill ${tarjetaEstado === 1 ? 'bg-success' : 'bg-secondary'}`}>
                                  {tarjetaEstado === 1 ? 'Activo' : 'Inactivo'}
                                </span>
                              );
                            })()}
                          </td>
                          <td className="text-center">
                            <div className="btn-group btn-group-sm">
                              {/* Botón Alta */}
                              <button 
                                className="btn btn-outline-success" 
                                title="Activar"
                                onClick={() => cambiarEstado(t.id, true)}
                              >
                                <i className="bi bi-check-circle"></i> Alta
                              </button>

                              {/* Botón Baja */}
                              <button 
                                className="btn btn-outline-warning" 
                                title="Desactivar"
                                onClick={() => cambiarEstado(t.id, false)}
                              >
                                <i className="bi bi-dash-circle"></i> Baja
                              </button>

                              {/* Botón Editar */}
                              <button className="btn btn-outline-primary" title="Editar" onClick={() => iniciarEdicion(t)}>
                                <i className="bi bi-pencil"></i> Editar
                              </button>
                              
                              {/* Botón Borrar */}
                              <button 
                                className="btn btn-outline-danger" 
                                title="Eliminar"
                                onClick={() => eliminarTarjeta(t.id)}
                              >
                                <i className="bi bi-trash"></i> Borrar
                              </button>
                            </div>
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
      </div>
    </div>
  );
}