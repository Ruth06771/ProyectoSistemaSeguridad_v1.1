import React from 'react';
import PermissionGate, { hasPermission } from '../../ui/PermissionGate';
export default function Roles({ onGoHome }) {
  const [roles, setRoles] = React.useState([]);
  const [name, setName] = React.useState('');
  const [desc, setDesc] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [msg, setMsg] = React.useState('');
  const canCreate = hasPermission('administracion.crear');
  const canEdit = hasPermission('administracion.editar');
  const canDelete = hasPermission('administracion.eliminar');

  const fetchRoles = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/roles', { credentials: 'include' });
      const data = await res.json();
      setRoles(Array.isArray(data) ? data : []);
    } catch (err) {
      setRoles([]);
    } finally { setLoading(false); }
  };

  React.useEffect(() => { fetchRoles(); }, []);

  const create = async () => {
    try {
      const res = await fetch('/api/roles', { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'include', body: JSON.stringify({ nombre: name, descripcion: desc }) });
      const data = await res.json();
      if (res.ok) { setMsg('Creado'); setName(''); setDesc(''); fetchRoles(); } else setMsg(data.error || 'Error');
    } catch (err) { setMsg('Error de red'); }
  };

  const remove = async (id) => {
    if (!confirm('Eliminar rol?')) return;
    try {
      const res = await fetch(`/api/roles/${id}`, { method: 'DELETE', credentials: 'include' });
      const data = await res.json();
      if (res.ok) { setMsg('Eliminado'); fetchRoles(); } else setMsg(data.error || 'Error');
    } catch (err) { setMsg('Error de red'); }
  };

  // Permisos management
  const [permisosList, setPermisosList] = React.useState([]);
  const fetchPermisos = async () => {
    try {
      const res = await fetch('/api/permisos', { credentials: 'include' });
      const data = await res.json();
      setPermisosList(Array.isArray(data) ? data : []);
    } catch (err) { setPermisosList([]); }
  };

  React.useEffect(() => { fetchPermisos(); }, []);

  const fetchPermisosDelRol = async (roleId) => {
    try {
      const res = await fetch(`/api/roles/${roleId}/permisos`, { credentials: 'include' });
      const data = await res.json();
      return Array.isArray(data) ? data : [];
    } catch (err) { return []; }
  };

  const assignPermiso = async (roleId, permisoId) => {
    try {
      const res = await fetch(`/api/roles/${roleId}/permisos`, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ permiso_id: permisoId }) });
      if (res.ok) { setMsg('Permiso asignado'); fetchRoles(); } else { const d = await res.json(); setMsg(d.error || 'Error'); }
    } catch (err) { setMsg('Error de red'); }
  };

  const unassignPermiso = async (roleId, permisoId) => {
    try {
      const res = await fetch(`/api/roles/${roleId}/permisos/${permisoId}`, { method: 'DELETE', credentials: 'include' });
      if (res.ok) { setMsg('Permiso quitado'); fetchRoles(); } else { const d = await res.json(); setMsg(d.error || 'Error'); }
    } catch (err) { setMsg('Error de red'); }
  };

  return (
    <div className="container py-4">
      <PermissionGate permissionKey="administracion.ver" fallback={
        <div className="alert alert-warning">Tu rol no tiene permisos para ver la gestión de roles.</div>
      }>
        <div className="card">
          <div className="card-header d-flex justify-content-between align-items-center">
            <h5 className="mb-0">Roles</h5>
            <button className="btn btn-sm btn-secondary" onClick={onGoHome}>Volver</button>
          </div>
          <div className="card-body">
            <PermissionGate permissionKey="administracion.crear" fallback={
              <div className="alert alert-warning mb-3">No tienes permisos para crear roles.</div>
            }>
              <div className="mb-3 d-flex gap-2">
                <input className="form-control" placeholder="Nombre rol" value={name} onChange={e => setName(e.target.value)} />
                <input className="form-control" placeholder="Descripción" value={desc} onChange={e => setDesc(e.target.value)} />
                <button className="btn btn-primary" onClick={create}>Crear</button>
              </div>
            </PermissionGate>
            {msg && <div className="alert alert-info">{msg}</div>}
          <hr />
          {loading ? <div className="empty-state"><span className="spinner-inline" /></div> : (
            roles.length === 0 ? <div className="empty-state">No hay roles</div> : (
              <ul className="list-group">
                {roles.map(r => (
                  <li key={r.id} className="list-group-item">
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <div className="fw-bold">{r.nombre}</div>
                        <div className="text-muted small">{r.descripcion}</div>
                      </div>
                      <div className="d-flex gap-2">
                        <PermissionGate permissionKey="administracion.editar" fallback={
                          <button className="btn btn-sm btn-outline-primary" disabled title="Sin permiso para editar permisos">Permisos</button>
                        }>
                          <button className="btn btn-sm btn-outline-primary" onClick={async () => {
                            const permisos = await fetchPermisosDelRol(r.id);
                            // show quick prompt to manage permisos
                            const permisoNames = permisos.map(p=>p.nombre).join(', ') || '—';
                            const add = confirm(`Permisos actuales: ${permisoNames}\n\n¿Quieres asignar un permiso nuevo a este rol? (Aceptar = asignar)`);
                            if (add) {
                              const options = permisosList.map(p => `${p.id}:${p.nombre}`).join('\n');
                              const pick = prompt(`Elige permiso a asignar (id:nombre)\n${options}`);
                              if (pick) {
                                const id = pick.split(':')[0];
                                await assignPermiso(r.id, Number(id));
                                fetchPermisos();
                                fetchRoles();
                              }
                            }
                          }}>Permisos</button>
                        </PermissionGate>
                        <PermissionGate permissionKey="administracion.eliminar" fallback={
                          <button className="btn btn-sm btn-danger" disabled title="Sin permiso para eliminar">Eliminar</button>
                        }>
                          <button className="btn btn-sm btn-danger" onClick={() => remove(r.id)}>Eliminar</button>
                        </PermissionGate>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )
          )}
        </div>
      </div>
    </PermissionGate>
  </div>
  );
}
