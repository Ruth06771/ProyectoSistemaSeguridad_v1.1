import React, { useState } from 'react';

export default function NuevaTarjetaRFID({ onSuccess, onCancel, tarjetas = [] }) {
  const [form, setForm] = useState({
    uid: '',
    nombre_completo: '',
    correo: '',
  });
  const [messages, setMessages] = useState([]);
  const [validated, setValidated] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setValidated(true);
    if (e.target.checkValidity()) {
      try {
        const res = await fetch('/api/tarjetas', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(form)
        });
        const data = await res.json();
        if (data.success) {
          setMessages([["success", "Tarjeta registrada correctamente"]]);
          if (onSuccess) onSuccess();
        } else {
          setMessages([["danger", data.error || "Error al registrar"]]);
        }
      } catch (err) {
        setMessages([["danger", "Error de red"]]);
      }
    }
  };

  return (
    <div className="container mt-5">
      <h2 className="mb-4">Registrar Nueva Tarjeta RFID</h2>
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
        <button type="submit" className="btn btn-primary">Guardar Tarjeta</button>
      </form>
      <h3 className="mt-5">Tarjetas Registradas</h3>
      <table className="table table-bordered">
        <thead>
          <tr>
            <th>UID</th>
            <th>Nombre Completo</th>
            <th>Correo</th>
          </tr>
        </thead>
        <tbody>
          {tarjetas.length > 0 ? tarjetas.map((tarjeta, i) => (
            <tr key={i}>
              <td>{tarjeta[0]}</td>
              <td>{tarjeta[1]}</td>
              <td>{tarjeta[2]}</td>
            </tr>
          )) : (
            <tr><td colSpan={3} className="text-center">Sin tarjetas registradas</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
