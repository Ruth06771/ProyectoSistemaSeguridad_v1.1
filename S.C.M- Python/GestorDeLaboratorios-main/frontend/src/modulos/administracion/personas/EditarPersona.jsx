import React, { useState, useEffect } from 'react';

export default function EditarPersona({ persona, onSubmit, onCancel, messages }) {
  const [form, setForm] = useState({
    nombre_completo: persona?.nombre_completo || '',
    fecha_nacimiento: persona?.fecha_nacimiento || '',
    correo: persona?.correo || '',
    telefono_personal: persona?.telefono_personal || '',
    documento_identidad: persona?.documento_identidad || '',
    sexo: persona?.sexo || '',
    tipo_sangre: persona?.tipo_sangre || '',
    persona_emergencia: persona?.persona_emergencia || '',
    telefono_emergencia: persona?.telefono_emergencia || '',
  });
  const [fechaError, setFechaError] = useState('');

  // Keep form in sync when persona prop arrives/changes (async fetch)
  useEffect(() => {
    setForm({
      nombre_completo: persona?.nombre_completo || '',
      fecha_nacimiento: persona?.fecha_nacimiento || '',
      correo: persona?.correo || '',
      telefono_personal: persona?.telefono_personal || '',
      documento_identidad: persona?.documento_identidad || '',
      sexo: persona?.sexo || '',
      tipo_sangre: persona?.tipo_sangre || '',
      persona_emergencia: persona?.persona_emergencia || '',
      telefono_emergencia: persona?.telefono_emergencia || '',
    });
    setFechaError('');
  }, [persona]);
  const [validated, setValidated] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    // Enforce max year for fecha_nacimiento client-side
    if (name === 'fecha_nacimiento') {
      if (value) {
        const year = parseInt(value.slice(0, 4), 10);
        if (!Number.isNaN(year) && year > 2025) {
          // clamp to max allowed date
          setFechaError('El año de nacimiento no puede ser mayor a 2025.');
          setForm({ ...form, [name]: '' });
          return;
        }
      }
      setFechaError('');
    }
    // For phone and documento fields allow only digits
    let v = value;
    if (name === 'telefono_personal' || name === 'documento_identidad' || name === 'telefono_emergencia') {
      v = value.replace(/\D/g, '');
    }
    setForm({ ...form, [name]: v });
    if (validated) setValidated(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setValidated(true);
    // Additional check for fecha_nacimiento year
    if (form.fecha_nacimiento) {
      const y = parseInt(form.fecha_nacimiento.slice(0, 4), 10);
      if (!Number.isNaN(y) && y > 2025) {
        setFechaError('El año de nacimiento no puede ser mayor a 2025.');
        return;
      }
    }

    if (e.target.checkValidity()) {
      onSubmit(form);
    }
  };

  return (
    <div className="container my-4">
      <h2 className="mb-4">Editar Persona</h2>
      {messages && messages.map(([category, msg], i) => (
        <div key={i} className={`alert alert-${category}`}>{msg}</div>
      ))}
      <form className={`needs-validation${validated ? ' was-validated' : ''}`} noValidate onSubmit={handleSubmit}>
        <div className="row g-3">
          <div className="col-md-6">
            <label className="form-label">Nombre Completo *</label>
            <input type="text" className="form-control" name="nombre_completo" required value={form.nombre_completo} onChange={handleChange} />
            <div className="invalid-feedback">Por favor ingresa el nombre completo.</div>
          </div>
          <div className="col-md-6">
            <label className="form-label">Fecha de Nacimiento *</label>
            <input type="date" className={`form-control ${fechaError ? 'is-invalid' : ''}`} name="fecha_nacimiento" required value={form.fecha_nacimiento} onChange={handleChange} max="2025-12-31" />
            {fechaError ? (
              <div className="invalid-feedback">{fechaError}</div>
            ) : (
              <div className="invalid-feedback">La fecha de nacimiento es obligatoria.</div>
            )}
          </div>
          <div className="col-md-6">
            <label className="form-label">Correo Electrónico *</label>
            <input type="email" className="form-control" name="correo" required value={form.correo} onChange={handleChange} />
            <div className="invalid-feedback">Introduce un correo válido.</div>
          </div>
          <div className="col-md-6">
            <label className="form-label">Teléfono Personal</label>
            <input type="text" pattern="\d*" inputMode="numeric" className="form-control" name="telefono_personal" value={form.telefono_personal} onChange={handleChange} />
          </div>
          <div className="col-md-6">
            <label className="form-label">Documento de Identidad *</label>
            <input type="text" pattern="\d*" inputMode="numeric" className="form-control" name="documento_identidad" required value={form.documento_identidad} onChange={handleChange} />
            <div className="invalid-feedback">El documento de identidad es obligatorio.</div>
          </div>
          <div className="col-md-6">
            <label className="form-label">Sexo *</label>
            <select className="form-select" name="sexo" required value={form.sexo} onChange={handleChange}>
              <option value="">-- Seleccione --</option>
              <option value="Masculino">Masculino</option>
              <option value="Femenino">Femenino</option>
              <option value="Otro">Otro</option>
            </select>
            <div className="invalid-feedback">Selecciona el sexo.</div>
          </div>
          <div className="col-md-6">
            <label className="form-label">Tipo de Sangre *</label>
            <select className="form-select" name="tipo_sangre" required value={form.tipo_sangre} onChange={handleChange}>
              <option value="">-- Seleccione --</option>
              <option value="A+">A+</option>
              <option value="A-">A-</option>
              <option value="B+">B+</option>
              <option value="B-">B-</option>
              <option value="AB+">AB+</option>
              <option value="AB-">AB-</option>
              <option value="O+">O+</option>
              <option value="O-">O-</option>
            </select>
            <div className="invalid-feedback">Selecciona el tipo de sangre.</div>
          </div>
          <div className="col-md-6">
            <label className="form-label">Persona de Emergencia *</label>
            <input type="text" className="form-control" name="persona_emergencia" required value={form.persona_emergencia} onChange={handleChange} />
            <div className="invalid-feedback">Ingresa el nombre de la persona de emergencia.</div>
          </div>
          <div className="col-md-6">
            <label className="form-label">Teléfono de Emergencia *</label>
            <input type="text" pattern="\d*" inputMode="numeric" className="form-control" name="telefono_emergencia" required value={form.telefono_emergencia} onChange={handleChange} />
            <div className="invalid-feedback">Ingresa un teléfono de emergencia válido.</div>
          </div>
        </div>
        <div className="mt-4 d-flex gap-2">
          <button type="button" className="btn btn-secondary" onClick={onCancel}>← Cancelar</button>
          <button type="submit" className="btn btn-primary">Guardar Cambios</button>
        </div>
      </form>
    </div>
  );
}
