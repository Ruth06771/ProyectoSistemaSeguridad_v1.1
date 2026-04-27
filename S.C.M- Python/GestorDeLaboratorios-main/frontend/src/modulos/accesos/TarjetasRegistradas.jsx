import React, { useState, useEffect } from 'react';
import NuevaTarjetaRFID from './NuevaTarjetaRFID';

function EditarTarjetaRFID({ id, onSuccess, onCancel }) {
  const [form, setForm] = useState({ uid: '', pin: '', estado: 1 });
  const [validated, setValidated] = useState(false);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    fetch(`/api/tarjetas/${id}`, { credentials: 'include' })
      .then(res => res.json())
      .then(data => setForm(data));
  }, [id]);

  const handleChange = e => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setValidated(true);
    if (e.target.checkValidity()) {
      const res = await fetch(`/api/tarjetas/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(form)
      });
      const data = await res.json();
      if (data.success) {
        setMessages([["success", "Tarjeta actualizada correctamente"]]);
        if (onSuccess) onSuccess();
      } else {
        setMessages([["danger", data.error || "Error al actualizar"]]);
      }
    }
  };

  return (
    <div className="container mt-5">
      <h2 className="mb-4">Editar Tarjeta RFID</h2>
      <button className="btn btn-secondary mb-3" onClick={onCancel}>
        ← Volver a Tarjetas Registradas
      </button>
      {messages.map(([cat, msg], i) => (
        <div key={i} className={`alert alert-${cat}`}>{msg}</div>
      ))}
      <form className={validated ? 'was-validated' : ''} noValidate onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">UID de la Tarjeta</label>
          <input type="text" name="uid" className="form-control" required value={form.uid} onChange={handleChange} />
        </div>
        <div className="mb-3">
          <label className="form-label">PIN (8 dígitos)</label>
          <input type="text" name="pin" className="form-control" required value={form.pin} onChange={handleChange} maxLength="8" />
        </div>
        <div className="mb-3">
          <label className="form-label">Estado</label>
          <div className="d-flex gap-2">
            <button
              type="button"
              className={`btn flex-grow-1 ${form.estado === 1 ? 'btn-success' : 'btn-outline-success'}`}
              onClick={() => setForm({...form, estado: 1})}
            >
              ✓ Activo
            </button>
            <button
              type="button"
              className={`btn flex-grow-1 ${form.estado === 0 ? 'btn-danger' : 'btn-outline-danger'}`}
              onClick={() => setForm({...form, estado: 0})}
            >
              ✕ Inactivo
            </button>
          </div>
        </div>
        <button type="submit" className="btn btn-primary">Guardar Cambios</button>
      </form>
    </div>
  );
}

export default function TarjetasRegistradas({ onGoHome }) {
  const [tarjetas, setTarjetas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState('list'); // 'list' | 'add' | 'edit'
  const [editId, setEditId] = useState(null);
  const [deleteMsg, setDeleteMsg] = useState('');

  // Cargar tarjetas
  const fetchTarjetas = () => {
    setLoading(true);
    fetch('/api/tarjetas', { credentials: 'include' })
      .then(res => res.json())
      .then(data => setTarjetas(data || []))
      .catch(() => setTarjetas([]))
      .finally(()=>setLoading(false));
  };

  useEffect(() => {
    if (view === 'list') fetchTarjetas();
  }, [view]);

  // Navegación
  const handleAdd = () => setView('add');
  const handleEdit = (id) => { setEditId(id); setView('edit'); };
  const handleBack = () => setView('list');

  // Eliminar tarjeta
  const handleDelete = async (id) => {
    if (!window.confirm('¿Seguro que deseas eliminar esta tarjeta?')) return;
    const res = await fetch(`/api/tarjetas/${id}`, {
      method: 'DELETE',
      credentials: 'include'
    });
    const data = await res.json();
    if (data.success) {
      setDeleteMsg('Tarjeta eliminada correctamente');
      fetchTarjetas();
    } else {
      setDeleteMsg(data.error || 'Error al eliminar');
    }
    setTimeout(() => setDeleteMsg(''), 2000);
  };

  // Toggle estado (cambiar activo/inactivo)
  const toggleEstado = async (tarjeta) => {
    const nuevoEstado = tarjeta.estado === 1 ? 0 : 1;
    const res = await fetch(`/api/tarjetas/${tarjeta.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ ...tarjeta, estado: nuevoEstado })
    });
    const data = await res.json();
    if (data.success) {
      fetchTarjetas();
      setDeleteMsg(`Estado actualizado a ${nuevoEstado === 1 ? 'Activo' : 'Inactivo'}`);
      setTimeout(() => setDeleteMsg(''), 2000);
    } else {
      setDeleteMsg(data.error || 'Error al actualizar estado');
    }
  };

  const getEstadoText = (estado) => estado === 1 ? 'Activo' : 'Inactivo';
  const getEstadoBadgeClass = (estado) => estado === 1 ? 'bg-success' : 'bg-secondary';

  if (view === 'add') {
    return <NuevaTarjetaRFID onSuccess={handleBack} onCancel={handleBack} onGoHome={onGoHome} />;
  }
  if (view === 'edit') {
    return <EditarTarjetaRFID id={editId} onSuccess={handleBack} onCancel={handleBack} onGoHome={onGoHome} />;
  }

  return (
    <div className="container py-4">
      <div className="card shadow-sm mb-4">
        <div className="card-header bg-primary text-white d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Tarjetas Registradas</h5>
          <span className="badge bg-info">{tarjetas.length} tarjetas</span>
        </div>
        <div className="card-body p-0">
          {deleteMsg && <div className="alert alert-info m-3">{deleteMsg}</div>}
          <div className="d-flex justify-content-end p-3">
            <button className="btn btn-primary" onClick={handleAdd}>
              <i className="bi bi-plus-circle me-2"></i> Nueva Tarjeta
            </button>
          </div>
          <div className="table-responsive">
            <table className="table table-striped table-hover align-middle mb-0">
              <thead className="table-dark">
                <tr>
                  <th>ID</th>
                  <th>UID</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={4} className="text-center py-4"><span className="spinner-inline" /></td></tr>
                ) : tarjetas.length > 0 ? (
                  tarjetas.map((fila, i) => (
                    <tr key={i}>
                      <td className="text-muted"><small>#{fila.id}</small></td>
                      <td><code style={{ fontSize: '12px', background: '#f8f9fa', padding: '4px 8px', borderRadius: '4px' }}>{fila.uid}</code></td>
                      <td><span className={`badge ${getEstadoBadgeClass(fila.estado)}`}>{getEstadoText(fila.estado)}</span></td>
                      <td>
                        <button
                          className="btn btn-sm btn-outline-info me-2"
                          title={fila.estado === 1 ? "Desactivar" : "Activar"}
                          onClick={() => toggleEstado(fila)}
                        >
                          <i className={`bi ${fila.estado === 1 ? 'bi-toggle-on' : 'bi-toggle-off'}`}></i>
                        </button>
                        <button className="btn btn-sm btn-warning me-2" title="Editar" onClick={() => handleEdit(fila.id)}>
                          <i className="bi bi-pencil-square"></i>
                        </button>
                        <button className="btn btn-sm btn-danger" title="Eliminar" onClick={() => handleDelete(fila.id)}>
                          <i className="bi bi-trash"></i>
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="text-center text-muted py-4">Sin tarjetas para mostrar</td>
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
