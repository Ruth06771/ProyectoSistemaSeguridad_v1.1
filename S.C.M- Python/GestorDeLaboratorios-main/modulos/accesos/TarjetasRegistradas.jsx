import React, { useState, useEffect } from 'react';
import NuevaTarjetaRFID from './NuevaTarjetaRFID';

function EditarTarjetaRFID({ id, onSuccess, onCancel, onEdited }) {
  const [form, setForm] = useState({ uid: '', nombre_completo: '', correo: '' });
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
        if (onEdited) onEdited();
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
          <label className="form-label">Nombre Completo</label>
          <input type="text" name="nombre_completo" className="form-control" required value={form.nombre_completo} onChange={handleChange} />
        </div>
        <div className="mb-3">
          <label className="form-label">Correo Electrónico</label>
          <input type="email" name="correo" className="form-control" required value={form.correo} onChange={handleChange} />
        </div>
        <button type="submit" className="btn btn-primary">Guardar Cambios</button>
      </form>
    </div>
  );
}

export default function TarjetasRegistradas() {
  const [tarjetas, setTarjetas] = useState([]);
  const [view, setView] = useState('list'); // 'list' | 'add' | 'edit'
  const [editId, setEditId] = useState(null);
  const [message, setMessage] = useState('');
  const [lastActionById, setLastActionById] = useState({});
  const [buscar, setBuscar] = useState('');

  // Cargar tarjetas
  const fetchTarjetas = () => {
    fetch('/api/tarjetas', { credentials: 'include' })
      .then(res => res.json())
      .then(setTarjetas)
      .catch(() => setTarjetas([]));
  };

  const getEstadoText = (estado) => estado === 1 ? 'Activo' : 'Inactivo';
  const getEstadoBadgeClass = (estado) => estado === 1 ? 'bg-success' : 'bg-secondary';
  const getAccionDisplay = (fila) => {
    if (lastActionById[fila.id]) return lastActionById[fila.id];
    if (fila.estado === 1 || fila.estado === '1' || fila.estado === true || fila.estado === 'Activo' || fila.estado === 'activo') return 'Alta';
    if (fila.estado === 0 || fila.estado === '0' || fila.estado === false || fila.estado === 'Inactivo' || fila.estado === 'inactivo') return 'Baja';
    return '-';
  };
  const getAccionBadgeClass = (accion) => {
    if (accion === 'Alta') return 'bg-success';
    if (accion === 'Baja') return 'bg-danger';
    if (accion === 'Editada') return 'bg-info';
    if (accion === 'Eliminada') return 'bg-danger';
    return 'bg-secondary';
  };

  const handleAccion = async (tarjeta, accion) => {
    if (accion === 'eliminada' && !window.confirm('¿Seguro que deseas eliminar esta tarjeta?')) return;

    if (accion === 'alta' || accion === 'baja') {
      const newEstado = accion === 'alta' ? 1 : 0;
      setTarjetas(prev => prev.map(t => t.id === tarjeta.id ? { ...t, estado: newEstado } : t));
    }

    try {
      const res = await fetch(`/api/tarjetas/${tarjeta.id}/accion`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ accion })
      });
      const data = await res.json();
      if (data.success) {
        setLastActionById(prev => ({
          ...prev,
          [tarjeta.id]: accion === 'editada' ? 'Editada' : accion === 'alta' ? 'Alta' : accion === 'baja' ? 'Baja' : accion === 'eliminada' ? 'Eliminada' : accion
        }));
        const mensajes = {
          alta: 'Tarjeta dada de Alta',
          baja: 'Tarjeta dada de Baja',
          eliminada: 'Tarjeta eliminada correctamente'
        };
        setMessage(mensajes[accion] || 'Acción realizada correctamente');
        if (accion === 'eliminada') {
          setTarjetas(prev => prev.filter(t => t.id !== tarjeta.id));
        }
      } else {
        setMessage(data.error || `Error al ejecutar acción ${accion}`);
        fetchTarjetas();
      }
    } catch (error) {
      setMessage('Error de conexión');
      fetchTarjetas();
    }
    setTimeout(() => setMessage(''), 2500);
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
      setMessage('Tarjeta eliminada correctamente');
      fetchTarjetas();
    } else {
      setMessage(data.error || 'Error al eliminar');
    }
    setTimeout(() => setMessage(''), 2000);
  };

  if (view === 'add') {
    return <NuevaTarjetaRFID onSuccess={handleBack} onCancel={handleBack} />;
  }
  if (view === 'edit') {
    return <EditarTarjetaRFID id={editId} onSuccess={handleBack} onEdited={() => setLastActionById(prev => ({ ...prev, [editId]: 'Editada' }))} onCancel={handleBack} />;
  }

  return (
    <div className="container py-4">
      <div className="card shadow-sm mb-4">
        <div className="card-header bg-primary text-white d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Tarjetas Registradas</h5>
          <span className="badge bg-info">{tarjetas.length} tarjetas</span>
        </div>
        <div className="card-body p-0">
          {message && <div className="alert alert-info m-3">{message}</div>}
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
                  <th>Nombre</th>
                  <th>Correo</th>
                  <th>Estado</th>
                  <th>Acción</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {tarjetas.length > 0 ? tarjetas.map((fila, i) => (
                  <tr key={i}>
                    <td>{fila.id}</td>
                    <td><span className="badge bg-secondary">{fila.uid}</span></td>
                    <td>{fila.nombre_completo}</td>
                    <td>{fila.correo}</td>
                    <td>
                      <span className={`badge ${getEstadoBadgeClass(fila.estado)}`}>
                        {getEstadoText(fila.estado)}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${getAccionBadgeClass(getAccionDisplay(fila))}`}>
                        {getAccionDisplay(fila)}
                      </span>
                    </td>
                    <td>
                      <div className="d-flex gap-1 flex-wrap">
                        <button
                          className={`btn btn-sm flex-fill ${fila.estado === 1 ? 'btn-success' : 'btn-outline-success'}`}
                          title="Alta"
                          onClick={() => handleAccion(fila, 'alta')}
                        >
                          Alta
                        </button>
                        <button
                          className={`btn btn-sm flex-fill ${fila.estado === 0 ? 'btn-danger' : 'btn-outline-danger'}`}
                          title="Baja"
                          onClick={() => handleAccion(fila, 'baja')}
                        >
                          Baja
                        </button>
                        <button
                          className="btn btn-sm btn-outline-danger flex-fill"
                          title="Eliminar"
                          onClick={() => handleAccion(fila, 'eliminada')}
                        >
                          Eliminada
                        </button>
                        <button className="btn btn-sm btn-warning flex-fill" title="Editar" onClick={() => handleEdit(fila.id)}>
                          <i className="bi bi-pencil-square"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={7} className="text-center text-muted py-4">
                      Sin tarjetas para mostrar
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
