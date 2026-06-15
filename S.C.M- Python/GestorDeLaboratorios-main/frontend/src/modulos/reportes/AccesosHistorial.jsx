 import React, { useState, useEffect, useMemo } from 'react';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';

export default function AccesosHistorial({ onFiltrar, resultados = [], filtros = {}, onExportExcel, onExportPDF, onVolver }) {
  const [form, setForm] = useState(filtros);
  const [activeFilter, setActiveFilter] = useState('');

  // Usar solo resultados dinámicos provistos por el backend
  const datosFinales = resultados || []; 

  useEffect(() => {
    if (onFiltrar) onFiltrar(filtros || {});
    if (filtros.tipo_movimiento) setActiveFilter('tipo_movimiento');
    else if (filtros.resultado) setActiveFilter('resultado');
    else if (filtros.credencial) setActiveFilter('credencial');
  }, []);

  const clearExclusiveFilters = (selectedName, nextForm) => {
    if (selectedName === 'tipo_movimiento') {
      return { ...nextForm, resultado: '', credencial: '' };
    }
    if (selectedName === 'resultado') {
      return { ...nextForm, tipo_movimiento: '', credencial: '' };
    }
    if (selectedName === 'credencial') {
      return { ...nextForm, tipo_movimiento: '', resultado: '' };
    }
    return nextForm;
  };

  const parseDateValue = value => {
    if (!value) return null;
    const normalized = value.includes('T') ? value.split('T')[0] : value.slice(0, 10);
    const date = new Date(normalized);
    return Number.isNaN(date.getTime()) ? null : date;
  };

  const filterResultados = (list, filters) => {
    const fromDate = parseDateValue(filters.fecha_desde);
    const toDate = parseDateValue(filters.fecha_hasta);

    return list.filter(row => {
      if (filters.tipo_movimiento && row.movimiento !== filters.tipo_movimiento) return false;
      if (filters.resultado && row.resultado !== filters.resultado) return false;
      if (filters.credencial && row.credencial !== filters.credencial) return false;

      const rowDateString = row.fecha_hora || row.fecha || '';
      const rowDate = parseDateValue(rowDateString);
      if ((fromDate || toDate) && !rowDate) return false;
      if (fromDate && rowDate < fromDate) return false;
      if (toDate && rowDate > toDate) return false;

      return true;
    });
  };

  const filteredResultados = useMemo(() => filterResultados(datosFinales, form), [datosFinales, form]);

  const handleChange = e => {
    const { name, value } = e.target;
    let nextForm = { ...form, [name]: value };

    if (['tipo_movimiento', 'resultado', 'credencial'].includes(name)) {
      nextForm = clearExclusiveFilters(name, nextForm);
      setActiveFilter(name);
    }

    setForm(nextForm);
    if (onFiltrar) onFiltrar(nextForm);
  };

  // Helper function to extract UID directly from data object
  // NO lee desde el DOM, sino desde el array de datos original
  // Busca la propiedad tarjeta_uid (backend), uid, tarjeta_id, o codigo_rfid
  const extractUIDFromData = (row) => {
    if (!row) return '';
    // Prioridad: tarjeta_uid (from backend) > uid > tarjeta_id > codigo_rfid
    return row.tarjeta_uid || row.uid || row.tarjeta_id || row.codigo_rfid || '';
  };

  const handleClear = () => {
    const emptyForm = {};
    setForm(emptyForm);
    setActiveFilter('');
    if (onFiltrar) onFiltrar(emptyForm);
  };

  /**
   * Exporta los datos filtrados a PDF con 8 columnas exactas
   * Fuente de datos: Array de objetos (filteredResultados), NO del DOM
   * Mapeo de columnas: ID, Fecha y Hora, Persona, Movimiento, Resultado, Credencial, UID Tarjeta, Descripción
   * Orientación: Landscape (horizontal) para que las 8 columnas tengan espacio
   */
  const handleExportPDF = () => {
    try {
      // Crear documento jsPDF con orientación landscape
      const doc = new jsPDF({ 
        orientation: 'landscape', 
        unit: 'pt', 
        format: 'letter',
        compress: true
      });

      // Encabezado del documento
      doc.setFontSize(16);
      doc.setFont(undefined, 'bold');
      doc.text('Historial de Accesos', 40, 30);

      // Fecha de generación
      doc.setFontSize(9);
      doc.setFont(undefined, 'normal');
      const now = new Date().toLocaleString('es-ES');
      doc.text(`Generado el: ${now}`, 40, 50);

      // Definir encabezados exactos (8 columnas) - hemos removido 'Movimiento'
      const tableHeaders = [
        ['ID', 'Fecha y Hora', 'Persona', 'Acción ESP', 'Resultado', 'Credencial', 'UID Tarjeta', 'Descripción']
      ];

      // Mapear datos del array filteredResultados (NO del DOM) a filas del PDF
      const tableRows = filteredResultados.map(row => [
        String(row.id || '').trim(),                              // Columna 1: ID
        String(row.fecha_hora || '').trim(),                      // Columna 2: Fecha y Hora
        String(row.persona || 'Desconocido').trim(),              // Columna 3: Persona
        String(row.accion || '').trim(),                          // Columna 4: Acción ESP
        String(row.resultado || '').trim(),                       // Columna 5: Resultado
        String(row.credencial || '').trim(),                      // Columna 6: Credencial
        String(extractUIDFromData(row) || '').trim(),             // Columna 7: UID Tarjeta (DESDE DATA, NO DOM)
        String(row.descripcion || '').trim()                      // Columna 8: Descripción
      ]);

      // Generar tabla con autoTable (jsPDF-autotable)
      doc.autoTable({
        startY: 70,
        head: tableHeaders,
        body: tableRows,
        
        // Estilos generales
        styles: {
          fontSize: 8,
          cellPadding: 4,
          overflow: 'linebreak',
          valign: 'middle',
          halign: 'left',
          font: 'helvetica'
        },
        
        // Estilos del encabezado
        headStyles: {
          fillColor: [51, 102, 153],      // Azul
          textColor: [255, 255, 255],     // Blanco
          fontStyle: 'bold',
          fontSize: 9,
          halign: 'center',
          valign: 'middle'
        },
        
        // Estilos alternados para filas
        alternateRowStyles: {
          fillColor: [242, 242, 242]      // Gris claro
        },
        
        // Estilos de columnas específicas
        columnStyles: {
          0: { cellWidth: 35, halign: 'center' },      // ID: centrado, 35pt
          1: { cellWidth: 95, halign: 'left' },        // Fecha: izq, 95pt
          2: { cellWidth: 110, halign: 'left' },       // Persona: izq, 110pt
          3: { cellWidth: 60, halign: 'center' },      // Acción ESP: centrado, 60pt
          4: { cellWidth: 60, halign: 'center' },      // Resultado: centrado, 60pt
          5: { cellWidth: 60, halign: 'center' },      // Credencial: centrado, 60pt
          6: { cellWidth: 85, halign: 'center' },      // UID Tarjeta: CENTRADO, 85pt
          7: { cellWidth: 120, halign: 'left' }        // Descripción: izq, 120pt
        },
        
        // Configuración de la tabla
        theme: 'grid',
        margin: { left: 15, right: 15, top: 70, bottom: 15 },
        didDrawPage: (data) => {
          // Pie de página
          const pageCount = doc.internal.getPages().length;
          doc.setFontSize(7);
          doc.text(
            `Página ${data.pageNumber} de ${pageCount}`,
            doc.internal.pageSize.getWidth() / 2,
            doc.internal.pageSize.getHeight() - 10,
            { align: 'center' }
          );
        }
      });

      // Guardar PDF con nombre descriptivo
      doc.save(`historial_accesos_${new Date().toISOString().split('T')[0]}.pdf`);

    } catch (error) {
      console.error('Error al generar PDF:', error);
      alert('Error al generar el PDF. Verifique que los datos estén disponibles.');
    }
  };

  const handleSelectFilter = type => {
    setActiveFilter(type);
    setForm(prevForm => clearExclusiveFilters(type, { ...prevForm, [type]: prevForm[type] || '' }));
  };

  return (
    <div className="container mt-4">
      <h2>Historial de Accesos</h2>
      <div className="text-start mb-3">
        <button className="btn btn-outline-secondary" onClick={onVolver}>
          ← Volver al Módulo de Reportes
        </button>
      </div>

      <div className="mb-3 d-flex flex-wrap gap-2">
        <button
          type="button"
          className={`btn ${activeFilter === 'tipo_movimiento' ? 'btn-primary' : 'btn-outline-primary'}`}
          onClick={() => handleSelectFilter('tipo_movimiento')}
        >
          Movimiento
        </button>
        <button
          type="button"
          className={`btn ${activeFilter === 'resultado' ? 'btn-primary' : 'btn-outline-primary'}`}
          onClick={() => handleSelectFilter('resultado')}
        >
          Resultado
        </button>
        <button
          type="button"
          className={`btn ${activeFilter === 'credencial' ? 'btn-primary' : 'btn-outline-primary'}`}
          onClick={() => handleSelectFilter('credencial')}
        >
          Credencial
        </button>
      </div>

      <form className="row g-3 mb-4">
        <div className="col-md-3">
          <label className="form-label">Fecha Desde</label>
          <input type="date" className="form-control" name="fecha_desde" value={form.fecha_desde || ''} onChange={handleChange} />
        </div>
        <div className="col-md-3">
          <label className="form-label">Fecha Hasta</label>
          <input type="date" className="form-control" name="fecha_hasta" value={form.fecha_hasta || ''} onChange={handleChange} />
        </div>
        <div className="col-md-2">
          <label className="form-label">Movimiento</label>
          <select className="form-select" name="tipo_movimiento" value={form.tipo_movimiento || ''} onChange={handleChange}>
            <option value="">-- Todos --</option>
            <option value="Entrada">Entrada</option>
            <option value="Salida">Salida</option>
          </select>
        </div>
        <div className="col-md-2">
          <label className="form-label">Resultado</label>
          <select className="form-select" name="resultado" value={form.resultado || ''} onChange={handleChange}>
            <option value="">-- Todos --</option>
            <option value="Permitido">Permitido</option>
            <option value="Denegado">Denegado</option>
          </select>
        </div>
        <div className="col-md-2">
          <label className="form-label">Credencial</label>
          <select className="form-select" name="credencial" value={form.credencial || ''} onChange={handleChange}>
            <option value="">-- Todos --</option>
            <option value="Tarjeta">Tarjeta</option>
            <option value="PIN">PIN</option>
          </select>
        </div>
        <div className="col-12 d-flex gap-2">
          <button
            type="button"
            className="btn btn-success flex-grow-1"
            onClick={() => onExportExcel ? onExportExcel(form) : null}
          >📥 Exportar a Excel</button>
          <button
            type="button"
            className="btn btn-danger flex-grow-1"
            onClick={() => onExportPDF ? onExportPDF(form) : handleExportPDF()}
          >📄 Exportar a PDF</button>
        </div>
      </form>

      <table className="table table-striped table-bordered table-hover">
        <thead className="table-dark">
          <tr>
              <th>ID</th>
              <th>Fecha y Hora</th>
              <th>Persona</th>
              <th>Acción</th>
              <th>Resultado</th>
              <th>Credencial</th>
              <th>UID Tarjeta</th>
              <th>Descripción</th>
            </tr>
        </thead>
        <tbody>
              {filteredResultados.length > 0 ? filteredResultados.map((row, i) => (
            <tr key={i}>
              <td>{row.id}</td>
              <td>{row.fecha_hora}</td>
              <td>{row.persona || 'Desconocido'}</td>
              <td>{row.accion || '-'}</td>
              <td>{row.resultado || '-'}</td>
              <td>{row.credencial || '-'}</td>
              <td>{extractUIDFromData(row) || '-'}</td>
              <td>{row.descripcion || '-'}</td>
            </tr>
          )) : (
            <tr><td colSpan={8} className="text-center">Sin resultados</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
