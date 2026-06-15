import React, { useState, useEffect } from 'react';

export default function Permisos({ onGoHome }) {
  const [roles, setRoles] = useState([]);
  const [permisos, setPermisos] = useState([]);
  const [rolSeleccionado, setRolSeleccionado] = useState(null);
  const [loadingRoles, setLoadingRoles] = useState(true);
  const [loadingPermisos, setLoadingPermisos] = useState(true);
  const [loadingPermisosDelRol, setLoadingPermisosDelRol] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [guardando, setGuardando] = useState(false);
  const acciones = ['Ver', 'Crear', 'Editar', 'Eliminar'];

  // Cargar roles al montar
  useEffect(() => {
    cargarRoles();
    cargarPermisos();
  }, []);

  // Cargar permisos del rol cuando cambia la selección
  useEffect(() => {
    if (rolSeleccionado) {
      cargarPermisosDelRol(rolSeleccionado);
    }
  }, [rolSeleccionado]);

  const cargarRoles = async () => {
    setLoadingRoles(true);
    try {
      const res = await fetch('/api/roles', { credentials: 'include' });
      if (!res.ok) throw new Error('Error al cargar roles');
      const data = await res.json();
      setRoles(Array.isArray(data) ? data : []);
      // Seleccionar el primer rol por defecto
      if (data.length > 0) {
        setRolSeleccionado(data[0].id);
      }
    } catch (err) {
      setMessage({ type: 'danger', text: `Error al cargar roles: ${err.message}` });
      setRoles([]);
    } finally {
      setLoadingRoles(false);
    }
  };

  const cargarPermisos = async () => {
    setLoadingPermisos(true);
    try {
      const res = await fetch('/api/permisos-modulos', { credentials: 'include' });
      if (!res.ok) throw new Error('Error al cargar permisos');
      const data = await res.json();
      setPermisos(Array.isArray(data) ? data : []);
    } catch (err) {
      setMessage({ type: 'danger', text: `Error al cargar permisos: ${err.message}` });
      setPermisos([]);
    } finally {
      setLoadingPermisos(false);
    }
  };

  const cargarPermisosDelRol = async (roleId) => {
    setLoadingPermisosDelRol(true);
    try {
      const res = await fetch(`/api/roles/${roleId}/permisos`, { credentials: 'include' });
      if (!res.ok) throw new Error('Error al cargar permisos del rol');
      const data = await res.json();
      if (!Array.isArray(data)) {
        throw new Error('Formato de permisos inválido');
      }
      const normalized = data.map(item => ({
        id: item.id,
        nombre: item.nombre,
        ver: Boolean(item.ver),
        crear: Boolean(item.crear),
        editar: Boolean(item.editar),
        eliminar: Boolean(item.eliminar),
        assigned: Boolean(item.assigned)
      }));
      setPermisos(normalized);
      if (normalized.length === 0) {
        setMessage({ type: 'info', text: 'El rol no tiene permisos asignados, mostrando tabla vacía.' });
      }
    } catch (err) {
      setMessage({ type: 'warning', text: `Error al cargar permisos del rol: ${err.message}` });
      setPermisos([]);
    } finally {
      setLoadingPermisosDelRol(false);
    }
  };

  const handleCheckboxChange = (permisoId, accion) => {
    setPermisos(prev => prev.map(p => {
      if (p.id !== permisoId) return p;
      return { ...p, [accion]: !Boolean(p[accion]) };
    }));
  };

  const guardarCambios = async () => {
    if (!rolSeleccionado) {
      setMessage({ type: 'warning', text: 'Selecciona un rol primero' });
      return;
    }

    setGuardando(true);
    setMessage({ type: '', text: '' });

    const payload = {
      permiso_matrix: permisos.map(p => ({
        id: p.id,
        ver: p.ver ? 1 : 0,
        crear: p.crear ? 1 : 0,
        editar: p.editar ? 1 : 0,
        eliminar: p.eliminar ? 1 : 0
      })),
      permiso_ids: permisos.filter(p => p.ver).map(p => p.id)
    };

    try {
      const res = await fetch(`/api/roles/${rolSeleccionado}/permisos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Error al guardar permisos');
      const data = await res.json();

      if (data.success) {
        setMessage({ type: 'success', text: '✓ Permisos guardados exitosamente' });
      } else {
        setMessage({ type: 'danger', text: `Error: ${data.error || 'No se pudieron guardar los permisos'}` });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: `Error de red: ${err.message}` });
    } finally {
      setGuardando(false);
    }
  };

  const restaurarPermisos = async () => {
    if (!rolSeleccionado) return;
    setLoadingPermisosDelRol(true);
    try {
      await cargarPermisosDelRol(rolSeleccionado);
      setMessage({ type: 'info', text: 'Permisos restaurados' });
    } finally {
      setLoadingPermisosDelRol(false);
    }
  };

  return (
    <div className="container py-4">
      <div className="card shadow-sm">
        <div className="card-header d-flex justify-content-between align-items-center bg-primary text-white">
          <h5 className="mb-0">Gestión de Permisos</h5>
          <button className="btn btn-sm btn-light" onClick={onGoHome}>Volver atrás</button>
        </div>

        <div className="card-body">
          {/* Selector de Rol */}
          <div className="mb-4">
            <label className="form-label fw-bold">Seleccionar Rol</label>
            {loadingRoles ? (
              <div className="spinner-border spinner-border-sm" role="status"><span className="visually-hidden">Cargando...</span></div>
            ) : roles.length === 0 ? (
              <div className="alert alert-warning">No hay roles disponibles</div>
            ) : (
              <select
                className="form-select w-100"
                value={rolSeleccionado || ''}
                onChange={e => setRolSeleccionado(Number(e.target.value))}
              >
                <option value="">-- Selecciona un rol --</option>
                {roles.map(r => (
                  <option key={r.id} value={r.id}>{r.nombre}</option>
                ))}
              </select>
            )}
          </div>

          {/* Mensaje de estado */}
          {message.text && (
            <div className={`alert alert-${message.type}`} role="alert">
              {message.text}
            </div>
          )}

          {/* Tabla de Permisos */}
          {loadingPermisos ? (
            <div className="text-center">
              <div className="spinner-border" role="status"><span className="visually-hidden">Cargando permisos...</span></div>
            </div>
          ) : permisos.length === 0 ? (
            <div className="alert alert-info">No hay permisos disponibles</div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover table-bordered align-middle">
                <thead className="table-dark">
                  <tr>
                    <th>Módulo / Permiso</th>
                    {acciones.map(a => <th key={a} className="text-center">{a}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {loadingPermisosDelRol ? (
                    <tr>
                      <td colSpan="5" className="text-center">
                        <div className="spinner-border spinner-border-sm" role="status">
                          <span className="visually-hidden">Cargando permisos del rol...</span>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    permisos.map(permiso => (
                      <tr key={permiso.id}>
                        <td>{permiso.nombre}</td>
                        <td className="text-center">
                          <input
                            type="checkbox"
                            className="form-check-input"
                            checked={Boolean(permiso.ver)}
                            onChange={() => handleCheckboxChange(permiso.id, 'ver')}
                          />
                        </td>
                        <td className="text-center">
                          <input
                            type="checkbox"
                            className="form-check-input"
                            checked={Boolean(permiso.crear)}
                            onChange={() => handleCheckboxChange(permiso.id, 'crear')}
                          />
                        </td>
                        <td className="text-center">
                          <input
                            type="checkbox"
                            className="form-check-input"
                            checked={Boolean(permiso.editar)}
                            onChange={() => handleCheckboxChange(permiso.id, 'editar')}
                          />
                        </td>
                        <td className="text-center">
                          <input
                            type="checkbox"
                            className="form-check-input"
                            checked={Boolean(permiso.eliminar)}
                            onChange={() => handleCheckboxChange(permiso.id, 'eliminar')}
                          />
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* Botones de Acción */}
          {rolSeleccionado && (
            <div className="mt-4 d-flex gap-2">
              <button
                className="btn btn-primary"
                onClick={guardarCambios}
                disabled={guardando || loadingPermisosDelRol}
              >
                {guardando ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Guardando...
                  </>
                ) : (
                  '💾 Guardar Cambios'
                )}
              </button>
              <button
                className="btn btn-outline-secondary"
                onClick={restaurarPermisos}
                disabled={guardando || loadingPermisosDelRol}
              >
                🔄 Restaurar
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
