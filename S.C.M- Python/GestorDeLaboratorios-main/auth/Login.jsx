import React, { useState } from 'react';

export default function Login({ onLoginSuccess }) {
  const [form, setForm] = useState({ correo: '', password: '' });
  const [error, setError] = useState('');
  const [validated, setValidated] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = e => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setValidated(true);
    if (e.target.checkValidity()) {
      setError('');
      setLoading(true);
      try {
        const res = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(form)
        });
        const data = await res.json();
        if (res.ok && data.success) {
          if (onLoginSuccess) onLoginSuccess(data);
        } else {
          setError(data.error || 'Error de autenticación');
        }
      } catch {
        setError('Error de red');
      }
      setLoading(false);
    }
  };

  return (
    <div className="bg-light min-vh-100 d-flex align-items-center justify-content-center">
      <div className="card shadow-lg" style={{ width: 400 }}>
        <div className="card-header text-center bg-primary text-white">
          <h4>Iniciar Sesión</h4>
        </div>
        <div className="card-body">
          {error && <div className="alert alert-danger">{error}</div>}
          <form noValidate className={validated ? 'was-validated' : ''} onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label">Correo electrónico</label>
              <input type="email" className="form-control" name="correo" required value={form.correo} onChange={handleChange} />
            </div>
            <div className="mb-3">
              <label className="form-label">Contraseña</label>
              <input type="password" className="form-control" name="password" required value={form.password} onChange={handleChange} />
            </div>
            <div className="d-grid">
              <button type="submit" className="btn btn-success" disabled={loading}>
                {loading ? <span className="spinner-border spinner-border-sm me-2"></span> : null}
                Ingresar
              </button>
            </div>
          </form>
        </div>
        <div className="card-footer text-center small">
          <span className="text-muted">¿Olvidaste tu contraseña?</span>
          <br />
          <button className="btn btn-link p-0" style={{ fontSize: '0.95em' }} disabled>
            Recuperar acceso (próximamente)
          </button>
          <hr className="my-2" />
          <span>Universidad Evangélica Boliviana - FCyT</span>
        </div>
      </div>
    </div>
  );
}
