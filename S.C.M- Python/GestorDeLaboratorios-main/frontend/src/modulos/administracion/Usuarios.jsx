import React, { useState, useEffect } from 'react';

export default function Usuarios({ onGoHome }) {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  // Estados del formulario de creación
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [creatingAdmin, setCreatingAdmin] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [adminUsuarios, setAdminUsuarios] = useState([]);
  const [loadingAdminUsuarios, setLoadingAdminUsuarios] = useState(false);

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

  const fetchAdminUsuarios = async () => {
    setLoadingAdminUsuarios(true);
    try {
      const res = await fetch('/api/admins', { credentials: 'include' });
      const data = await res.json();
      setAdminUsuarios(Array.isArray(data) ? data : []);
    } catch (err) {
      setAdminUsuarios([]);
    } finally {
      setLoadingAdminUsuarios(false);
    }
  };

  useEffect(() => { fetchUsuarios(); fetchAdminUsuarios(); }, []);

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

  const deleteUsuario = async (id) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar este usuario?')) {
      return;
    }
    try {
      const res = await fetch(`/api/personas/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      const data = await res.json();
      if (data.success) {
        setMessage({ type: 'success', text: 'Usuario eliminado correctamente.' });
        fetchUsuarios();
      } else {
        setMessage({ type: 'danger', text: `Error al eliminar usuario: ${data.error || 'Desconocido'}` });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: 'Error de red al eliminar usuario.' });
    }
  };

  const deleteAdminUsuario = async (id) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar este acceso directo?')) {
      return;
    }
    try {
      const res = await fetch(`/api/admins/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      const data = await res.json();
      if (data.success) {
        setMessage({ type: 'success', text: 'Acceso directo eliminado correctamente.' });
        fetchAdminUsuarios();
      } else {
        setMessage({ type: 'danger', text: `Error al eliminar acceso directo: ${data.error || 'Desconocido'}` });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: 'Error de red al eliminar acceso directo.' });
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCreateAdmin = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });

    // Validación básica
    if (!formData.email.trim() || !formData.password.trim()) {
      setMessage({ type: 'warning', text: 'Por favor completa todos los campos.' });
      return;
    }

    setCreatingAdmin(true);
    try {
      const res = await fetch('/api/admins/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          email: formData.email.trim().toLowerCase(),
          password: formData.password
        })
      });

      const data = await res.json();

      if (data.success) {
        setMessage({ type: 'success', text: '✓ Administrador creado exitosamente.' });
        // Limpiar formulario
        setFormData({ email: '', password: '' });
        // Refrescar tablas de usuarios y accesos directos
        fetchUsuarios();
        fetchAdminUsuarios();
      } else {
        const errorText = data.error === 'invalid_email'
          ? 'Formato de correo inválido.'
          : data.error === 'email_domain_not_allowed'
          ? 'El dominio del correo no está permitido.'
          : data.error === 'limit_reached'
          ? 'Se alcanzó el máximo de administradores (5).'
          : data.error === 'exists_or_error'
          ? 'El usuario ya existe o hubo un error.'
          : data.message || 'Error desconocido.';
        setMessage({ type: 'danger', text: `✗ ${errorText}` });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: '✗ Error de red al crear administrador.' });
    } finally {
      setCreatingAdmin(false);
    }
  };

  return (
    <div className="container py-4">
      {/* Formulario de Creación de Admin */}
      <div className="card shadow-sm mb-4">
        <div className="card-header bg-primary text-white">
          <h5 className="mb-0">Crear Nuevo Usuario</h5>
        </div>
        <div className="card-body">
          <form onSubmit={handleCreateAdmin}>
            <div className="row">
              <div className="col-md-5 mb-3">
                <label htmlFor="email" className="form-label">Correo Institucional</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  className="form-control"
                  placeholder="admin@ueb.edu.bo"
                  value={formData.email}
                  onChange={handleFormChange}
                  disabled={creatingAdmin}
                  required
                />
              </div>
              <div className="col-md-5 mb-3">
                <label htmlFor="password" className="form-label">Contraseña</label>
                <div style={{ position: 'relative', display: 'block', width: '100%' }}>
                  <input
                    type={showPassword ? "text" : "password"}
                    id="password"
                    name="password"
                    className="form-control"
                    placeholder="Ingresa contraseña"
                    value={formData.password}
                    onChange={handleFormChange}
                    disabled={creatingAdmin}
                    required
                    style={{ paddingRight: '45px', width: '100%' }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{
                      position: 'absolute',
                      right: '12px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      color: '#000000',
                      fontWeight: 'bold',
                      fontSize: '13px',
                      zIndex: 10
                    }}
                  >
                    {showPassword ? "Ocultar" : "Ver"}
                  </button>
                </div>
              </div>
              <div className="col-md-2 d-flex align-items-end mb-3 justify-content-center">
                <button
                  type="submit"
                  className="btn btn-success w-100"
                  disabled={creatingAdmin}
                >
                  {creatingAdmin ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Guardando...
                    </>
                  ) : (
                    'Guardar en Sistema'
                  )}
                </button>
              </div>
            </div>
          </form>
          
          {message.text && (
            <div className={`alert alert-${message.type} mt-3 mb-0`} role="alert">
              {message.text}
            </div>
          )}
        </div>
      </div>

      <div className="card shadow-sm mb-4">
        <div className="card-header bg-secondary text-white">
          <h6 className="mb-0">Usuarios del Sistema (usuario_sistema)</h6>
        </div>
        <div className="card-body">
          {loadingAdminUsuarios ? (
            <p>Cargando accesos directos...</p>
          ) : adminUsuarios.length === 0 ? (
            <p>No hay usuarios directos en usuario_sistema.</p>
          ) : (
            <ul className="list-group">
              {adminUsuarios.map((admin) => (
                <li key={admin.id} className="list-group-item d-flex justify-content-between align-items-center">
                  <span>{admin.nombre_usuario} <small className="text-muted">(Clave: {admin.contrasena})</small></span>
                  <button type="button" className="btn btn-sm btn-outline-danger" onClick={() => deleteAdminUsuario(admin.id)}>
                    Eliminar
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Tabla de Usuarios */}
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
                    <th>Acciones</th>
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
                        <div className="d-flex gap-2">
                          <select className="form-select form-select-sm d-inline-block w-auto" defaultValue={u.rol || 'estudiante'} onChange={(e) => changeRole(u.id, e.target.value)}>
                            <option value="administrador">Administrador</option>
                            <option value="docente">Docente</option>
                            <option value="estudiante">Estudiante</option>
                            <option value="auxiliar">Auxiliar</option>
                            <option value="invitado">Invitado</option>
                          </select>
                          <button type="button" className="btn btn-sm btn-danger" onClick={() => deleteUsuario(u.id)}>
                            Eliminar
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
  );
}
