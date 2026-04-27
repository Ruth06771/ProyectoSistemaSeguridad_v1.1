import React, { useState } from 'react';

export default function RegistrarPersona({ onSuccess, onCancel, onGoHome }) {
  const [form, setForm] = useState({
    nombre_completo: '',
    fecha_nacimiento: '',
    correo: '',
    telefono_personal: '',
    documento_identidad: '',
    sexo: '',
    tipo_sangre: '',
    rol: 'estudiante',
    contactos_emergencia: [
      { persona_emergencia: '', telefono_emergencia: '', emergencia_relacion: '', emergencia_direccion: '' }
    ]
  });

  const [messages, setMessages] = useState([]);
  const [validated, setValidated] = useState(false);
  const [fechaError, setFechaError] = useState('');

  // 🔹 Maneja cambios generales
  const handleChange = (e) => {
    const { name, value } = e.target;
    // Enforce max year for fecha_nacimiento
    if (name === 'fecha_nacimiento') {
      if (value) {
        const year = parseInt(value.slice(0, 4), 10);
        if (!Number.isNaN(year) && year > 2025) {
          setFechaError('El año de nacimiento no puede ser mayor a 2025.');
          setForm({ ...form, [name]: '' });
          return;
        }
      }
      setFechaError('');
    }
    // For phone and documento fields allow only digits
    let v = value;
    if (name === 'telefono_personal' || name === 'documento_identidad') {
      v = value.replace(/\D/g, '');
    }
    setForm({ ...form, [name]: v });
    if (validated) setValidated(false);
  };

  // 🔹 Maneja cambios dentro de cada contacto
  const handleEmergenciaChange = (index, e) => {
    const { name, value } = e.target;
    const nuevosContactos = [...form.contactos_emergencia];
    let v = value;
    if (name === 'telefono_emergencia') v = value.replace(/\D/g, '');
    nuevosContactos[index][name] = v;
    setForm({ ...form, contactos_emergencia: nuevosContactos });
    if (validated) setValidated(false);
  };

  // 🔹 Agregar un nuevo contacto
  const agregarContacto = () => {
    setForm({
      ...form,
      contactos_emergencia: [
        ...form.contactos_emergencia,
        { persona_emergencia: '', telefono_emergencia: '', emergencia_relacion: '', emergencia_direccion: '' }
      ]
    });
  };

  // 🔹 Eliminar un contacto
  const eliminarContacto = (index) => {
    const nuevosContactos = form.contactos_emergencia.filter((_, i) => i !== index);
    setForm({ ...form, contactos_emergencia: nuevosContactos });
  };

  // 🔹 Enviar formulario
  const handleSubmit = async (e) => {
    e.preventDefault();
    setValidated(true);
    // validate fecha_nacimiento year
    if (form.fecha_nacimiento) {
      const y = parseInt(form.fecha_nacimiento.slice(0, 4), 10);
      if (!Number.isNaN(y) && y > 2025) {
        setFechaError('El año de nacimiento no puede ser mayor a 2025.');
        return;
      }
    }
    if (e.target.checkValidity()) {
      try {
        const res = await fetch('/api/personas', {
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

      <div className="d-flex gap-2 mb-4">
        <button className="btn btn-secondary" onClick={onCancel}>← Volver al listado</button>
        <button className="btn btn-outline-primary" onClick={onGoHome}>🏠 Volver al inicio</button>
      </div>

      {messages.map(([cat, msg], i) => (
        <div key={i} className={`alert alert-${cat}`}>{msg}</div>
      ))}

      <form noValidate className={validated ? 'was-validated' : ''} onSubmit={handleSubmit}>
        <div className="row g-3">
          {/* --- DATOS PERSONALES --- */}
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
            <label className="form-label">Teléfono Personal *</label>
            <input type="tel" pattern="\d*" inputMode="numeric" className="form-control" name="telefono_personal" required value={form.telefono_personal} onChange={handleChange} />
            <div className="invalid-feedback">Introduce un teléfono válido (sólo dígitos).</div>
          </div>

          <div className="col-md-6">
            <label className="form-label">Número de Carnet *</label>
            <input type="text" pattern="\d*" inputMode="numeric" className="form-control" name="documento_identidad" required value={form.documento_identidad} onChange={handleChange} />
            <div className="invalid-feedback">El número de carnet es obligatorio.</div>
          </div>

          <div className="col-md-6">
            <label className="form-label">Sexo *</label>
            <select className="form-select" name="sexo" required value={form.sexo} onChange={handleChange}>
              <option value="">Selecciona...</option>
              <option value="Masculino">Masculino</option>
              <option value="Femenino">Femenino</option>
              <option value="Prefiero no decirlo">Prefiero no decirlo</option>
            </select>
            <div className="invalid-feedback">Selecciona el sexo.</div>
          </div>

          <div className="col-md-6">
            <label className="form-label">Tipo de Sangre *</label>
            <select className="form-select" name="tipo_sangre" required value={form.tipo_sangre} onChange={handleChange}>
              <option value="">Selecciona...</option>
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



          
          <div className="col-12 mt-4">
            <h5>Contactos de emergencia</h5>
          </div>

          {form.contactos_emergencia.map((contacto, index) => (
            <div key={index} className="border rounded p-3 mb-3">
              <div className="row g-3 align-items-end">
                <div className="col-md-6">
                  <label className="form-label">Nombre contacto *</label>
                  <input
                    type="text"
                    className="form-control"
                    name="persona_emergencia"
                    value={contacto.persona_emergencia}
                    onChange={(e) => handleEmergenciaChange(index, e)}
                    required
                  />
                  <div className="invalid-feedback">Nombre del contacto es obligatorio.</div>
                </div>

                <div className="col-md-6">
                  <label className="form-label">Teléfono de emergencia *</label>
                  <input
                    type="tel"
                    pattern="\d*"
                    inputMode="numeric"
                    className="form-control"
                    name="telefono_emergencia"
                    value={contacto.telefono_emergencia}
                    onChange={(e) => handleEmergenciaChange(index, e)}
                    required
                  />
                  <div className="invalid-feedback">Teléfono de emergencia obligatorio (sólo dígitos).</div>
                </div>

                <div className="col-md-6">
                  <label className="form-label">Relación *</label>
                  <input
                    type="text"
                    className="form-control"
                    name="emergencia_relacion"
                    value={contacto.emergencia_relacion}
                    onChange={(e) => handleEmergenciaChange(index, e)}
                    required
                  />
                  <div className="invalid-feedback">Indica la relación con la persona.</div>
                </div>

                <div className="col-md-6">
                  <label className="form-label">Dirección *</label>
                  <input
                    type="text"
                    className="form-control"
                    name="emergencia_direccion"
                    value={contacto.emergencia_direccion}
                    onChange={(e) => handleEmergenciaChange(index, e)}
                    required
                  />
                  <div className="invalid-feedback">La dirección es obligatoria.</div>
                </div>
                
                {form.contactos_emergencia.length > 1 && (
                  <div className="col-12">
                    <button
                      type="button"
                      className="btn btn-danger btn-sm mt-2"
                      onClick={() => eliminarContacto(index)}
                    >
                      🗑 Eliminar este contacto
                    </button>
                  </div>
                )}
              </div>
            </div>
            
          ))}


          <div className="col-12">
            <button type="button" className="btn btn-outline-success" onClick={agregarContacto}>
              ➕ Agregar otro contacto
            </button>
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

