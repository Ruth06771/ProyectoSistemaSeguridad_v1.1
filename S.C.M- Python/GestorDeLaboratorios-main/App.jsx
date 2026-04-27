import React, { useState, useEffect } from 'react';
import Login from './auth/Login';
import AdminDashboard from './dashboard/AdminDashboard';

export default function App() {
  const [usuario, setUsuario] = useState(null);
  const [rol, setRol] = useState(null);
  const [loading, setLoading] = useState(true);

  // Verifica sesión al cargar
  useEffect(() => {
    fetch('/api/session', { credentials: 'include' })
      .then(res => res.ok ? res.json() : { usuario: null })
      .then(data => {
        setUsuario(data.usuario);
        setRol(data.rol);
        setLoading(false);
      });
  }, []);

  // Login exitoso
  const handleLoginSuccess = (data) => {
    setUsuario(data.usuario);
    setRol(data.rol);
  };

  // Logout
  const handleLogout = async () => {
    await fetch('/api/logout', { method: 'POST', credentials: 'include' });
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
