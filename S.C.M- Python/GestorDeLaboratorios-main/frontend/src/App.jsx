import React, { useState, useEffect } from 'react';
import Login from './auth/Login';
import AdminDashboard from './dashboard/AdminDashboard';

export default function App() {
  const [usuario, setUsuario] = useState(null);
  const [rol, setRol] = useState(null);
  const [loading, setLoading] = useState(true);

  const saveSessionToStorage = (data) => {
    if (!data) return;
    if (data.permissions) localStorage.setItem('permissions', JSON.stringify(data.permissions));
    if (data.permission_modules) localStorage.setItem('permission_modules', JSON.stringify(data.permission_modules));
    if (data.rol) localStorage.setItem('rol', data.rol);
    if (data.nombre) localStorage.setItem('nombre', data.nombre);
    if (data.usuario) localStorage.setItem('usuario', data.usuario);
  };

  // Verifica sesión al cargar
  useEffect(() => {
    fetch('/api/session', { credentials: 'include' })
      .then(res => res.ok ? res.json() : { usuario: null })
      .then(data => {
        if (data && data.usuario) {
          setUsuario(data.usuario);
          setRol(data.rol);
          saveSessionToStorage(data);
        }
        setLoading(false);
      });
  }, []);

  // Login exitoso
  const handleLoginSuccess = (data) => {
    setUsuario(data.usuario);
    setRol(data.rol);
    saveSessionToStorage(data);
  };

  // Logout
  const handleLogout = async () => {
    await fetch('/api/logout', { method: 'POST', credentials: 'include' });
    localStorage.removeItem('permissions');
    localStorage.removeItem('permission_modules');
    localStorage.removeItem('rol');
    localStorage.removeItem('nombre');
    localStorage.removeItem('usuario');
    setUsuario(null);
    setRol(null);
  };

  if (loading) return <div className="text-center mt-5">Cargando...</div>;

  if (!usuario) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  // Puedes expandir aquí para mostrar diferentes dashboards según el rol
  return <AdminDashboard usuario={usuario} onLogout={handleLogout} />;
}
