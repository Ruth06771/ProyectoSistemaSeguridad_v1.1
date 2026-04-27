import React, { useState } from 'react';

export default function RegistrarPersonaEmergencia({ onSaved, onCancel }) {
  const [form, setForm] = useState({
    nombre_completo: '',
    telefono_emergencia: '',
    tipo_sangre: '',
    persona_emergencia: '',
    emergencia_relacion: '',
    emergencia_direccion: ''
  });
  const [msg, setMsg] = useState('');

  const handleChange = e => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSave = async () => {
    setMsg('Guardando...');
    try {
      const res = await fetch('/api/personas-emergencia', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
        credentials: 'include'
      });
      const j = await res.json();
      if (res.ok) {
        setMsg('Guardado correctamente');
        if (onSaved) onSaved();
        setTimeout(() => onCancel && onCancel(), 700);
      } else {
        setMsg('Error: ' + (j.error || j.message || 'Desconocido'));
      }
    } catch (err) {
      setMsg('Error de conexión');
    }
  };

  return (
    <div className="container py-3">
      <h5 className="mb-3">Registrar Persona de Emergencia</h5>

      <input name="nombre_completo" className="form-control mb-2" placeholder="Nombre completo" value={form.nombre_completo} onChange={handleChange} />
      <input name="telefono_emergencia" className="form-control mb-2" placeholder="Teléfono de emergencia" value={form.telefono_emergencia} onChange={handleChange} />
      <input name="tipo_sangre" className="form-control mb-2" placeholder="Tipo de sangre" value={form.tipo_sangre} onChange={handleChange} />
      <input name="persona_emergencia" className="form-control mb-2" placeholder="Contacto de emergencia" value={form.persona_emergencia} onChange={handleChange} />
      <input name="emergencia_relacion" className="form-control mb-2" placeholder="Relación" value={form.emergencia_relacion} onChange={handleChange} />
      <input name="emergencia_direccion" className="form-control mb-2" placeholder="Dirección" value={form.emergencia_direccion} onChange={handleChange} />

      {msg && <div className="alert alert-info mt-2">{msg}</div>}

      <div className="d-flex gap-2 mt-2">
        <button className="btn btn-secondary" onClick={onCancel}>Cancelar</button>
        <button className="btn btn-primary" onClick={handleSave}>Guardar</button>
      </div>
    </div>
  );
}