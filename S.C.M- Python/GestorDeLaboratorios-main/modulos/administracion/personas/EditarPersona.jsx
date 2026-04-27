import React, { useState } from 'react';

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
  const [validated, setValidated] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setValidated(true);
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
            <input type="text" pattern="\d*" className="form-control" name="telefono_personal" value={form.telefono_personal} onChange={handleChange} />
          </div>
          <div className="col-md-6">
            <label className="form-label">Documento de Identidad *</label>
            <input type="text" className="form-control" name="documento_identidad" required value={form.documento_identidad} onChange={handleChange} />
          </div>
          <div className="col-md-6">
            <label className="form-label">Sexo *</label>
            <select className="form-select" name="sexo" required value={form.sexo} onChange={handleChange}>
              <option value="">-- Seleccione --</option>
              <option value="Masculino">Masculino</option>
              <option value="Femenino">Femenino</option>
              <option value="Otro">Otro</option>
            </select>
          </div>
          <div className="col-md-6">
            <label className="form-label">Tipo de Sangre</label>
            <input type="text" className="form-control" name="tipo_sangre" value={form.tipo_sangre} onChange={handleChange} />
          </div>
          <div className="col-md-6">
            <label className="form-label">Persona de Emergencia *</label>
            <input type="text" className="form-control" name="persona_emergencia" required value={form.persona_emergencia} onChange={handleChange} />
          </div>
          <div className="col-md-6">
            <label className="form-label">Teléfono de Emergencia *</label>
            <input type="text" pattern="\d*" className="form-control" name="telefono_emergencia" required value={form.telefono_emergencia} onChange={handleChange} />
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
