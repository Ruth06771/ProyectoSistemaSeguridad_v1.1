import React from 'react';

export default function ReporteTarjetasPDF({ rows = [] }) {
  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ textAlign: 'center' }}>Reporte de Altas y Bajas de Tarjetas RFID</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ backgroundColor: '#cccccc' }}>
            <th style={{ border: '1px solid #000', padding: 4 }}>ID</th>
            <th style={{ border: '1px solid #000', padding: 4 }}>UID</th>
            <th style={{ border: '1px solid #000', padding: 4 }}>Nombre</th>
            <th style={{ border: '1px solid #000', padding: 4 }}>Acción</th>
            <th style={{ border: '1px solid #000', padding: 4 }}>Ejecutado por</th>
            <th style={{ border: '1px solid #000', padding: 4 }}>Fecha y Hora</th>
          </tr>
        </thead>
        <tbody>
          {rows.length > 0 ? rows.map((row, i) => (
            <tr key={i}>
              <td style={{ border: '1px solid #000', padding: 4 }}>{row.id}</td>
              <td style={{ border: '1px solid #000', padding: 4 }}>{row.uid}</td>
              <td style={{ border: '1px solid #000', padding: 4 }}>{row.nombre_completo}</td>
              <td style={{ border: '1px solid #000', padding: 4 }}>{row.accion}</td>
              <td style={{ border: '1px solid #000', padding: 4 }}>{row.ejecutado_por}</td>
              <td style={{ border: '1px solid #000', padding: 4 }}>{row.ejecutado_en}</td>
            </tr>
          )) : (
            <tr><td colSpan={6} style={{ textAlign: 'center', border: '1px solid #000', padding: 4 }}>Sin datos</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
