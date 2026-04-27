import React, { useState } from 'react';

export default function Permisos({ onGoHome }) {
  const roles = ['Administrador', 'Auxiliar'];

  const modulos = [
    'Configuración',
    'Enrolar',
    'Seguridad',
    'Reportes'
  ];

  const acciones = ['Ver', 'Crear', 'Editar', 'Eliminar'];

  const permisosIniciales = {
    'Administrador': {
      Configuración: { Ver: true, Crear: true, Editar: true, Eliminar: true },
      Enrolar: { Ver: true, Crear: true, Editar: true, Eliminar: true },
      Seguridad: { Ver: true, Crear: true, Editar: true, Eliminar: true },
      Reportes: { Ver: true, Crear: true, Editar: true, Eliminar: true },
    },
    'Auxiliar': {
      Configuración: { Ver: false, Crear: false, Editar: false, Eliminar: false },
      Enrolar: { Ver: false, Crear: false, Editar: false, Eliminar: false },
      Seguridad: { Ver: true, Crear: false, Editar: true, Eliminar: false },
      Reportes: { Ver: true, Crear: false, Editar: true, Eliminar: false },
    },
  };

  const [rolSeleccionado, setRolSeleccionado] = useState('Administrador');
  const [permisos, setPermisos] = useState(permisosIniciales);

  const handleChange = (modulo, accion) => {
    setPermisos(prev => ({
      ...prev,
      [rolSeleccionado]: {
        ...prev[rolSeleccionado],
        [modulo]: {
          ...prev[rolSeleccionado][modulo],
          [accion]: !prev[rolSeleccionado][modulo][accion],
        },
      },
    }));
  };

  const guardarCambios = () => {
    alert(`Permisos actualizados para ${rolSeleccionado}`);
  // debug log removed in cleanup
  };

  return (
    <div className="container py-4">
      <div className="card">
        <div className="card-header d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Gestión de Permisos</h5>
          <button className="btn btn-sm btn-secondary" onClick={onGoHome}>Volver atras</button>
        </div>

        <div className="card-body">
          <div className="mb-3">
            <label className="form-label">Seleccionar Rol</label>
            <select
              className="form-select w-auto"
              value={rolSeleccionado}
              onChange={e => setRolSeleccionado(e.target.value)}
            >
              {roles.map(r => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          <table className="table table-bordered align-middle">
            <thead className="table-dark">
              <tr>
                <th>Módulo</th>
                {acciones.map(a => <th key={a}>{a}</th>)}
              </tr>
            </thead>
            <tbody>
              {modulos.map(mod => (
                <tr key={mod}>
                  <td><strong>{mod}</strong></td>
                  {acciones.map(acc => (
                    <td key={acc} className="text-center">
                      <input
                        type="checkbox"
                        checked={permisos[rolSeleccionado][mod][acc]}
                        onChange={() => handleChange(mod, acc)}
                        disabled={rolSeleccionado === 'Administrador'} // Admin tiene todo fijo
                      />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>

          <div className="mt-3 d-flex gap-2">
            <button className="btn btn-primary" onClick={guardarCambios}>
              💾 Guardar Cambios
            </button>
            <button className="btn btn-outline-secondary" onClick={() => setPermisos(permisosIniciales)}>
              🔄 Restaurar Valores
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
