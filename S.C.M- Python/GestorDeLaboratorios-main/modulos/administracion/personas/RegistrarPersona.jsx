import React, { useState } from 'react';

export default function RegistrarPersona({ onSuccess, onCancel }) {
  const [form, setForm] = useState({
    nombre_completo: '',
    fecha_nacimiento: '',
    correo: '',
    telefono_personal: '',
    documento_identidad: '',
    sexo: '',
    tipo_sangre: '',
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
        const res = await fetch('/api/persona', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form)
        });
        const data = await res.json();
        if (data.success) {
          setMessages([["success", "Persona registrada correctamente"]]);
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
    <div className="container mt-4">
      <h2 className="mb-4">Registrar Nueva Persona</h2>
      <button className="btn btn-secondary mb-4" onClick={onCancel}>
        ← Volver al listado de personas
      </button>
      {messages.map(([cat, msg], i) => (
        <div key={i} className={`alert alert-${cat}`}>{msg}</div>
      ))}
      <form noValidate className={validated ? 'was-validated' : ''} onSubmit={handleSubmit}>
        <div className="row g-3">
          <div className="col-md-6">
            <label className="form-label">Nombre Completo *</label>
            <input type="text" className="form-control" name="nombre_completo" required value={form.nombre_completo} onChange={handleChange} />
          </div>
          <div className="col-md-6">
            <label className="form-label">Fecha de Nacimiento *</label>
            <input type="date" className="form-control" name="fecha_nacimiento" required value={form.fecha_nacimiento} onChange={handleChange} />
          </div>
          <div className="col-md-6">
            <label className="form-label">Correo Electrónico *</label>
            <input type="email" className="form-control" name="correo" required value={form.correo} onChange={handleChange} />
          </div>
          <div className="col-md-6">
            <label className="form-label">Teléfono Personal</label>
            <input type="tel" pattern="\d*" className="form-control" name="telefono_personal" value={form.telefono_personal} onChange={handleChange} />
          </div>
          <div className="col-md-6">
            <label className="form-label">Número de Carnet *</label>
            <input type="text" className="form-control" name="documento_identidad" required value={form.documento_identidad} onChange={handleChange} />
          </div>
          <div className="col-md-6">
            <label className="form-label">Sexo *</label>
            <select className="form-select" name="sexo" required value={form.sexo} onChange={handleChange}>
              <option value="">Selecciona...</option>
              <option value="Masculino">Masculino</option>
              <option value="Femenino">Femenino</option>
              <option value="Otro">Otro</option>
            </select>
          </div>
          <div className="col-md-6">
            <label className="form-label">Tipo de Sangre</label>
            <select className="form-select" name="tipo_sangre" value={form.tipo_sangre} onChange={handleChange}>
              <option value="">No especificado</option>
              <option value="A+">A+</option>
              <option value="A-">A-</option>
              <option value="B+">B+</option>
              <option value="B-">B-</option>
              <option value="AB+">AB+</option>
              <option value="AB-">AB-</option>
              <option value="O+">O+</option>
              <option value="O-">O-</option>
            </select>
          </div>
        </div>
        <div className="mt-4 d-flex gap-2">
          <button type="button" className="btn btn-secondary" onClick={onCancel}>← Cancelar</button>
          <button type="submit" className="btn btn-primary">Registrar</button>
        </div>
      </form>
    </div>
  );
}
