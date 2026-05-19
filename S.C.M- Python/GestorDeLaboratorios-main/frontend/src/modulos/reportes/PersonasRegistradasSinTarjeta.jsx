/**
 * Componente PersonasRegistradasSinTarjeta - Historial de Registro de Personas
 *
 * CAMBIOS PERMANENTES IMPLEMENTADOS:
 * - Estilos CSS incrustados directamente en el componente para evitar problemas de caché
 * - Encabezado oscuro y botones de colores aplicados con !important
 * - Función de carga de datos actualizada para usar estilos consistentes
 * - Versión 2.0.0 para forzar refresco del navegador
 * - Archivo fuente real modificado - no vista temporal
 */

import React, { useState, useEffect, useMemo } from 'react';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';
import * as XLSX from 'xlsx';

export default function PersonasRegistradasSinTarjeta({ onVolver }) {
  // Versión del componente para forzar refresco del navegador
  const COMPONENT_VERSION = '2.0.0';
  const [resultados, setResultados] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({});

  // Estilos incrustados para asegurar que se apliquen permanentemente
  const estilosIncrustados = `
    <style>
      /* Estilos específicos para PersonasRegistradasSinTarjeta */
      .personas-registradas-container h2 {
        color: #000101;
        font-weight: 600;
        margin-bottom: 1rem;
      }

      .personas-registradas-container .btn-outline-secondary {
        border-color: #6c757d;
        color: #6c757d;
      }

      .personas-registradas-container .btn-outline-secondary:hover {
        background-color: #6c757d;
        color: white;
      }

      .personas-registradas-container .btn-primary {
        background-color: #0d6efd;
        border-color: #0d6efd;
        color: white;
      }

      .personas-registradas-container .btn-primary:hover {
        background-color: #0b5ed7;
        border-color: #0a58ca;
      }

      .personas-registradas-container .btn-secondary {
        background-color: #6c757d;
        border-color: #6c757d;
        color: white;
      }

      .personas-registradas-container .btn-success {
        background-color: #198754;
        border-color: #198754;
        color: white;
      }

      .personas-registradas-container .btn-danger {
        background-color: #dc3545;
        border-color: #dc3545;
        color: white;
      }

      .personas-registradas-container .table-dark {
        background-color: #212529 !important;
        color: white !important;
      }

      .personas-registradas-container .table-dark th {
        background-color: #212529 !important;
        color: white !important;
        border-color: #343a40 !important;
        font-weight: 600;
      }

      .personas-registradas-container .table-striped tbody tr:nth-of-type(odd) {
        background-color: rgba(0, 0, 0, 0.05);
      }

      .personas-registradas-container .table-hover tbody tr:hover {
        background-color: rgba(0, 0, 0, 0.075);
      }

      .personas-registradas-container .alert-danger {
        background-color: #f8d7da;
        border-color: #f5c2c7;
        color: #721c24;
      }

      .personas-registradas-container .alert-info {
        background-color: #d1ecf1;
        border-color: #bee5eb;
        color: #0c5460;
      }

      .personas-registradas-container .spinner-border.text-primary {
        color: #0d6efd !important;
      }

      .personas-registradas-container .form-control:focus {
        border-color: #0d6efd;
        box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
      }

      /* Forzar aplicación de estilos incluso con cache */
      .personas-registradas-container .table {
        border-collapse: collapse;
        width: 100%;
      }

      .personas-registradas-container .table th,
      .personas-registradas-container .table td {
        padding: 0.75rem;
        vertical-align: top;
        border-top: 1px solid #dee2e6;
      }

      .personas-registradas-container .table thead th {
        vertical-align: bottom;
        border-bottom: 2px solid #dee2e6;
      }
    </style>
  `;

  const normalizeAccionValue = (accion) => {
    if (accion === undefined || accion === null) return null;
    return String(accion).trim();
  };

  const getAccionValue = (row) => {
    return normalizeAccionValue(row?.accion ?? row?.Accion ?? row?.action);
  };

  // Función para mapear acciones a español
  const mapAccion = (accion) => {
    const value = normalizeAccionValue(accion);
    if (!value) return 'Desconocido';
    const a = value.toLowerCase();
    switch (a) {
      case 'create':
      case 'crear':
      case 'alta':
      case 'activar':
      case 'activate':
      case 'activo':
        return 'Activo';
      case 'update':
      case 'editar':
      case 'edicion':
      case 'edición':
      case 'edit':
        return 'Editado';
      case 'delete':
      case 'borrar':
      case 'eliminar':
      case 'eliminado':
        return 'Eliminado';
      case 'deactivate':
      case 'desactivar':
      case 'inhabilitar':
      case 'inactivar':
      case 'inactivo':
      case 'baja':
        return 'Inactivo';
      default:
        return value;
    }
  };

  // Cargar datos al montar el componente
  useEffect(() => {
    cargarDatos();
  }, []);

  // Función para cargar datos desde la API
  const cargarDatos = async (filtros = {}) => {
    try {
      setLoading(true);
      setError(null);

      // Construir query string con filtros
      const params = new URLSearchParams();
      if (filtros.buscar) params.append('buscar', filtros.buscar);
      if (filtros.nombre_persona) params.append('nombre', filtros.nombre_persona);
      if (filtros.responsable) params.append('responsable', filtros.responsable);
      if (filtros.fecha_desde) params.append('fecha_desde', filtros.fecha_desde);

      const url = `/api/reportes/personas-registradas-sin-tarjeta${params.toString() ? '?' + params.toString() : ''}`;

      const response = await fetch(url, {
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setResultados(data);
    } catch (err) {
      console.error('Error al cargar datos:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Función para parsear fechas
  const parseDateValue = value => {
    if (!value) return null;
    const normalized = value.includes('T') ? value.split('T')[0] : value.slice(0, 10);
    const date = new Date(normalized);
    return Number.isNaN(date.getTime()) ? null : date;
  };

  const formatDateTime = value => {
    if (!value) return '';
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? '' : date.toLocaleString('es-BO');
  };

  // Función para filtrar resultados (ahora solo para filtrado local si es necesario)
  const filterResultados = (list, filters) => {
    const fromDate = parseDateValue(filters.fecha_desde);

    return list.filter(row => {
      // Filtro por identificación
      if (filters.buscar) {
        const searchLower = filters.buscar.toLowerCase();
        const documento = (row.documento_identidad || '').toLowerCase();
        if (!documento.includes(searchLower)) {
          return false;
        }
      }

      // Filtro por nombre de la persona
      if (filters.nombre_persona) {
        const nombreLower = filters.nombre_persona.toLowerCase();
        const nombre = (row.nombre_completo || '').toLowerCase();
        if (!nombre.includes(nombreLower)) {
          return false;
        }
      }

      // Filtro por responsable
      if (filters.responsable) {
        const responsableLower = filters.responsable.toLowerCase();
        const usuario = (row.usuario || 'Sistema').toLowerCase();
        if (!usuario.includes(responsableLower)) {
          return false;
        }
      }

      // Filtro por fecha
      const rowDateString = row.fecha_hora || '';
      const rowDate = parseDateValue(rowDateString);
      if (fromDate && !rowDate) return false;
      if (fromDate && rowDate < fromDate) return false;

      return true;
    });
  };

  // useMemo para filtrado reactivo
  const filteredResultados = useMemo(() => filterResultados(resultados, form), [resultados, form]);

  // Manejo de cambios en los inputs
  const handleChange = e => {
    const { name, value } = e.target;
    const nextForm = { ...form, [name]: value };
    setForm(nextForm);
    // No necesitamos llamar a onFiltrar aquí, el filtrado se hace localmente
  };

  // Refrescar la lista actual de personas
  const handleRefresh = () => {
    cargarDatos(form);
  };

  // Limpiar todos los filtros
  const handleClear = () => {
    const emptyForm = {};
    setForm(emptyForm);
    // Recargar todos los datos sin filtros
    cargarDatos(emptyForm);
  };

  // Aplicar filtros (botón de búsqueda)
  const handleFiltrar = () => {
    cargarDatos(form);
  };

  // Exportar a Excel
  const handleExportExcel = () => {
    try {
      const worksheetData = filteredResultados.map(row => ({
        'ID': row.id || '',
        'Identificación': row.documento_identidad || '',
        'Nombre Completo': row.nombre_completo || '',
        'Fecha y Hora': formatDateTime(row.fecha_hora),
        'Responsable': row.usuario || 'Sistema',
        'Accion': mapAccion(getAccionValue(row))
      }));

      const worksheet = XLSX.utils.json_to_sheet(worksheetData);
      
      // Ajustar ancho de columnas
      worksheet['!cols'] = [
        { wch: 6 },   // ID
        { wch: 15 },  // Identificación
        { wch: 25 },  // Nombre Completo
        { wch: 20 },  // Fecha y Hora
        { wch: 20 },  // Responsable
        { wch: 15 }   // Accion
      ];

      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Personas Sin Tarjeta');
      
      const fileName = `personas_registradas_sin_tarjeta_${new Date().toISOString().split('T')[0]}.xlsx`;
      XLSX.writeFile(workbook, fileName);
    } catch (error) {
      console.error('Error al exportar a Excel:', error);
      alert('Error al exportar a Excel.');
    }
  };

  // Exportar a PDF
  const handleExportPDF = () => {
    try {
      const doc = new jsPDF({
        orientation: 'portrait',
        unit: 'pt',
        format: 'letter',
        compress: true
      });

      const pageWidth = doc.internal.pageSize.getWidth ? doc.internal.pageSize.getWidth() : doc.internal.pageSize.width;
      const pageHeight = doc.internal.pageSize.getHeight ? doc.internal.pageSize.getHeight() : doc.internal.pageSize.height;

      // Encabezado
      doc.setFontSize(16);
      doc.setFont(undefined, 'bold');
      doc.text('Historial de Registro de Personas', 40, 30);

      // Fecha de generación
      doc.setFontSize(9);
      doc.setFont(undefined, 'normal');
      const now = new Date().toLocaleString('es-ES');
      doc.text(`Generado el: ${now}`, 40, 50);

      // Definir encabezados (6 columnas)
      const tableHeaders = [
        ['ID', 'Identificación', 'Nombre Completo', 'Fecha y Hora', 'Responsable', 'Accion']
      ];

      // Mapear datos filtrados
      const tableRows = filteredResultados.map(row => [
        String(row.id || '').trim(),
        String(row.documento_identidad || '').trim(),
        String(row.nombre_completo || '').trim(),
        String(formatDateTime(row.fecha_hora)).trim(),
        String(row.usuario || 'Sistema').trim(),
        String(mapAccion(getAccionValue(row))).trim()
      ]);

      // Generar tabla
      doc.autoTable({
        startY: 70,
        head: tableHeaders,
        body: tableRows,
        styles: {
          fontSize: 9,
          cellPadding: 5,
          overflow: 'linebreak',
          valign: 'middle',
          halign: 'left',
          font: 'helvetica'
        },
        headStyles: {
          fillColor: [51, 102, 153],
          textColor: [255, 255, 255],
          fontStyle: 'bold',
          fontSize: 10,
          halign: 'center',
          valign: 'middle'
        },
        alternateRowStyles: {
          fillColor: [242, 242, 242]
        },
        columnStyles: {
          0: { cellWidth: 25, halign: 'center' },
          1: { cellWidth: 50, halign: 'left' },
          2: { cellWidth: 90, halign: 'left' },
          3: { cellWidth: 70, halign: 'left' },
          4: { cellWidth: 60, halign: 'left' },
          5: { cellWidth: 50, halign: 'left' }
        },
        theme: 'grid',
        margin: { left: 15, right: 15, top: 70, bottom: 15 },
        didDrawPage: (data) => {
          const pageCount = doc.internal.getNumberOfPages ? doc.internal.getNumberOfPages() : (doc.internal.pages ? Object.keys(doc.internal.pages).length : 1);
          doc.setFontSize(7);
          doc.text(
            `Página ${data.pageNumber} de ${pageCount}`,
            pageWidth / 2,
            pageHeight - 10,
            { align: 'center' }
          );
        }
      });

      const fileName = `historial_personas_${new Date().toISOString().split('T')[0]}.pdf`;
      doc.save(fileName);
    } catch (error) {
      console.error('Error al generar PDF:', error);
      alert('Error al exportar a PDF.');
    }
  };

  return (
    <>
      {/* Estilos incrustados para asegurar aplicación permanente */}
      <div dangerouslySetInnerHTML={{ __html: estilosIncrustados }} />

      <div className="container mt-4 personas-registradas-container">
        <h2 style={{ color: '#000' }}>📋 Historial de Registro de Personas</h2>
        <div className="text-start mb-3 d-flex flex-wrap gap-2">
          <button
            className="btn btn-outline-secondary"
            onClick={onVolver}
            title="Regresar al panel de informes"
          >
            <span className="me-1">←</span> Volver a Reportes
          </button>
          <button
            type="button"
            className="btn btn-outline-primary"
            onClick={handleRefresh}
            disabled={loading}
            title="Refrescar la lista"
          >
            🔄 Refrescar
          </button>
        </div>

      {/* Mostrar error si existe */}
      {error && (
        <div className="alert alert-danger">
          <strong>Error:</strong> {error}
          <button 
            className="btn btn-sm btn-outline-danger ms-2" 
            onClick={() => cargarDatos(form)}
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Filtros Reactivos */}
      <form className="row g-3 mb-4 align-items-end" onSubmit={(e) => { e.preventDefault(); handleFiltrar(); }}>
        <div className="col-lg-3 col-md-6">
          <label className="form-label">Identificación</label>
          <input
            type="text"
            className="form-control"
            name="buscar"
            value={form.buscar || ''}
            onChange={handleChange}
            placeholder="Buscar por cédula"
          />
        </div>

        <div className="col-lg-3 col-md-6">
          <label className="form-label">Nombre de la Persona</label>
          <input
            type="text"
            className="form-control"
            name="nombre_persona"
            value={form.nombre_persona || ''}
            onChange={handleChange}
            placeholder="Nombre de la persona"
          />
        </div>

        <div className="col-lg-3 col-md-6">
          <label className="form-label">Responsable del Registro</label>
          <input
            type="text"
            className="form-control"
            name="responsable"
            value={form.responsable || ''}
            onChange={handleChange}
            placeholder="Usuario responsable"
          />
        </div>

        <div className="col-lg-3 col-md-6">
          <label className="form-label">Desde (Fecha)</label>
          <input
            type="date"
            className="form-control"
            name="fecha_desde"
            value={form.fecha_desde || ''}
            onChange={handleChange}
          />
        </div>

        <div className="col-12 d-flex">
          
          <button
            type="button"
            className="btn btn-success"
            onClick={handleExportExcel}
            disabled={filteredResultados.length === 0 || loading}
            style={{ width: '50%' }}
          >
            📥 Exportar a Excel
          </button>
          <button
            type="button"
            className="btn btn-danger"
            onClick={handleExportPDF}
            disabled={filteredResultados.length === 0 || loading}
            style={{ width: '50%' }}
          >
            📄 Exportar a PDF
          </button>
        </div>
      </form>

      {/* Indicador de carga */}
      {loading && (
        <div className="text-center my-4">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando...</span>
          </div>
          <p className="mt-2">Cargando datos...</p>
        </div>
      )}

      {/* Tabla de resultados */}
      {!loading && (
        <div className="table-responsive">
          <table className="table table-striped table-bordered table-hover">
            <thead className="table-dark">
              <tr>
                <th>ID</th>
                <th>Identificación</th>
                <th>Nombre Completo</th>
                <th>Fecha y Hora</th>
                <th>Responsable</th>
                <th>Accion</th>
              </tr>
            </thead>
            <tbody>
              {filteredResultados.length > 0 ? (
                filteredResultados.map((row, i) => (
                  <tr key={i}>
                    <td className="fw-bold">{row.id || '-'}</td>
                    <td>{row.documento_identidad || '-'}</td>
                    <td>{row.nombre_completo || '-'}</td>
                    <td>
                      {row.fecha_hora
                        ? new Date(row.fecha_hora).toLocaleString('es-BO')
                        : 'Sin registro'}
                    </td>
                    <td>{row.usuario ? row.usuario : 'Sistema'}</td>
                    <td>{mapAccion(getAccionValue(row))}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="text-center text-muted">
                    {error ? 'Error al cargar datos' : 'Sin resultados - No hay personas registradas que coincidan con los filtros'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Resumen de resultados */}
      {!loading && resultados.length > 0 && (
        <div className="alert alert-info mt-3">
          <strong>Registros encontrados:</strong> {filteredResultados.length} de {resultados.length}
        </div>
      )}
      </div>
    </>
  );
}
