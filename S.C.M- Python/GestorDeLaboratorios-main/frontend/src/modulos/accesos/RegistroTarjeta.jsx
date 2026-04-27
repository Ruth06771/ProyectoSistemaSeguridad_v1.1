import React, { useState, useEffect } from 'react';

export default function RegistroTarjeta({ onGoHome }) {
  const [form, setForm] = useState({ uid: '', pin: '', estado: 1 });
  const [msg, setMsg] = useState('');
  const [tarjetas, setTarjetas] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch('/api/tarjetas', { credentials: 'include' })
      .then(r => r.json())
      .then(data => setTarjetas(data))
      .catch(() => setTarjetas([]))
      .finally(() => setLoading(false));
  }, []);

  const submit = async () => {
    if (!form.uid || form.uid.trim() === '') { setMsg('UID es obligatorio'); return; }
    if (!/^\d{8}$/.test((form.pin || '').toString().trim())) { setMsg('El PIN debe tener exactamente 8 dígitos'); return; }
    setMsg('Guardando...');
    try {
      const res = await fetch('/api/tarjetas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
        credentials: 'include'
      });
      const j = await res.json();
      if (res.ok) {
        setMsg('✓ Tarjeta registrada exitosamente');
        const t = await fetch('/api/tarjetas', { credentials: 'include' }).then(r => r.json());
        setTarjetas(t || []);
        setForm({ uid: '', pin: '', estado: 1 });
        setTimeout(() => setMsg(''), 3000);
      } else {
        setMsg(j.message || j.error || 'Error al guardar');
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

      <div className="row g-4">
        {/* Columna izquierda: Formulario */}
        <div className="col-lg-6">
          <div className="card mb-3">
            <div className="card-header">Registro de Tarjeta</div>
            <div className="card-body">
              {/* UID */}
              <div className="mb-3">
                <label className="form-label">UID <span className="text-danger">*</span></label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Ej: A1B2C3D4"
                  value={form.uid}
                  onChange={e => setForm({...form, uid: e.target.value})}
                />
              </div>

              {/* PIN */}
              <div className="mb-3">
                <label className="form-label">PIN <span className="text-danger">*</span></label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Ej: 12345678"
                  value={form.pin}
                  onChange={e => setForm({...form, pin: e.target.value})}
                  maxLength="8"
                />
                <small className="text-muted">Exactamente 8 dígitos numéricos</small>
              </div>

              {/* Estado */}
              <div className="mb-4">
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

              {/* Botón Guardar */}
              <button className="btn btn-primary w-100" onClick={submit}>
                Guardar Tarjeta
              </button>

              {/* Mensaje */}
              {msg && (
                <div className={`alert ${msg.includes('✓') ? 'alert-success' : msg.includes('Error') || msg.includes('debe') ? 'alert-danger' : 'alert-info'} mt-3 mb-0`}>
                  {msg}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Columna derecha: Tabla */}
        <div className="col-lg-6">
          <div className="card">
            <div className="card-header">Tarjetas Registradas</div>
            <div className="card-body p-0">
              {loading ? (
                <div className="text-center py-5"><span className="spinner-border text-primary" role="status"></span></div>
              ) : tarjetas.length === 0 ? (
                <div className="text-center text-muted py-5">No hay tarjetas registradas</div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover align-middle mb-0">
                    <thead className="table-light">
                      <tr>
                        <th style={{ width: '50px' }}>ID</th>
                        <th>UID</th>
                        <th style={{ width: '100px' }}>Estado</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tarjetas.slice(-10).map(t => (
                        <tr key={t.id}>
                          <td className="text-muted"><small>#{t.id}</small></td>
                          <td><code>{t.uid}</code></td>
                          <td><span className={`badge ${getEstadoBadgeClass(t.estado)}`}>{getEstadoText(t.estado)}</span></td>
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
