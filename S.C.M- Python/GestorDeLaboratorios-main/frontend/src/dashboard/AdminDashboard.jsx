import React, { useState, useEffect } from 'react';
import './dashboard.css';
import StatCard from './StatCard';
import { FaUser, FaIdCard, FaDoorOpen } from 'react-icons/fa';
import Personas from '../modulos/administracion/personas/Personas';
import TarjetasRegistradas from '../modulos/accesos/TarjetasRegistradas';
import AccesosHistorial from '../modulos/reportes/AccesosHistorial';
import TarjetasHistorial from '../modulos/reportes/TarjetasHistorial';
import Usuarios from '../modulos/administracion/Usuarios';
import RegistroTarjeta from '../modulos/accesos/RegistroTarjeta';
import TipoMovimiento from '../modulos/registro/TipoMovimiento';
import TipoRegistro from '../modulos/registro/TipoRegistro';
import PerfilPersona from '../modulos/enrolar/PerfilPersona';
import Enrolar from '../modulos/enrolar/Enrolar';
import BitacoraViewer from '../modulos/administracion/BitacoraViewer';
import ReportesIngresos from '../modulos/reportes/ReportesIngresos';
import PersonasRegistradasSinTarjeta from '../modulos/reportes/PersonasRegistradasSinTarjeta';
import Permisos from '../modulos/administracion/Permisos';
import Roles from '../modulos/administracion/Roles';
import Dispositivos from '../modulos/administracion/Dispositivos';
import TopNav from '../ui/TopNav';

export default function AdminDashboard({ usuario, onLogout }) {
  const [view, setView] = useState('dashboard'); // views include new module names
  // Sidebar removed: layout uses TopNav (horizontal navigation)

  // Estados para reportes
  const [resultadosAccesos, setResultadosAccesos] = useState([]);
  const [filtrosAccesos, setFiltrosAccesos] = useState({});

  const [resultadosTarjetas, setResultadosTarjetas] = useState([]);
  const [filtrosTarjetas, setFiltrosTarjetas] = useState({});

  const [resultadosPersonasSinTarjeta, setResultadosPersonasSinTarjeta] = useState([]);
  const [filtrosPersonasSinTarjeta, setFiltrosPersonasSinTarjeta] = useState({});

  // Helpers
  const buildQuery = (obj) => {
    const params = new URLSearchParams();
    Object.keys(obj || {}).forEach(k => {
      const v = obj[k];
      if (v !== undefined && v !== null && String(v).trim() !== '') params.append(k, v);
    });
    return params.toString();
  };

  // Dashboard stats
  const [stats, setStats] = useState({ personas: 0, tarjetas: 0, accesos: 0 });
  const [ultimosAccesos, setUltimosAccesos] = useState([]);
  const [ultimosTarjetas, setUltimosTarjetas] = useState([]);
  const [loadingStats, setLoadingStats] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      setLoadingStats(true);
      try {
        const mRes = await fetch('/api/metrics', { credentials: 'include' });
        const metrics = await mRes.json();
        setStats({ personas: metrics.personas || 0, tarjetas: metrics.tarjetas || 0, accesos: metrics.accesos || 0 });
        // Peticiones para últimos elementos (limitadas por el backend a lo seguro)
        const [tRes, aRes] = await Promise.all([
          fetch('/api/tarjetas', { credentials: 'include' }),
          fetch('/api/reportes/accesos_historial', { credentials: 'include' })
        ]);
        const [tJson, aJson] = await Promise.all([tRes.json(), aRes.json()]);
        setUltimosAccesos(Array.isArray(aJson) ? (aJson.slice(0, 8)) : []);
        setUltimosTarjetas(Array.isArray(tJson) ? (tJson.slice(0, 8)) : []);
      } catch (err) {
        setStats({ personas: 0, tarjetas: 0, accesos: 0 });
        setUltimosAccesos([]);
      } finally {
        setLoadingStats(false);
      }
    };
    fetchStats();
  }, []);

  // Auto-cargar datos de tarjetas cuando se navega a la vista de historial
  useEffect(() => {
    if (view === 'tarjetas_historial' && resultadosTarjetas.length === 0) {
      fetchTarjetas({});
    }
  }, [view]);

  // Auto-cargar datos de accesos cuando se navega a la vista de historial
  useEffect(() => {
    if (view === 'accesos_historial' && resultadosAccesos.length === 0) {
      fetchAccesos({});
    }
  }, [view]);

  // Fetch reportes
  const fetchAccesos = async (filtros = {}) => {
    setFiltrosAccesos(filtros);
    const q = buildQuery(filtros);
    // Add cache-busting parameter
    const timestamp = new Date().getTime();
    const separator = q ? '&' : '?';
    const url = `/api/reportes/accesos_historial${q ? `?${q}` : ''}${separator}_t=${timestamp}`;
    try {
      const res = await fetch(url, { credentials: 'include' });
      const data = await res.json();
      // normalize response: backend may return array or { value: [...], Count }
      const rows = Array.isArray(data) ? data : (data && data.value ? data.value : []);
      setResultadosAccesos(rows || []);
    } catch (err) {
      setResultadosAccesos([]);
    }
  };

  const fetchTarjetas = async (filtros = {}) => {
    setFiltrosTarjetas(filtros);
    try {
      const q = buildQuery(filtros);
      const timestamp = new Date().getTime();
      const separator = q ? '&' : '?';
      const url = `/api/reportes/tarjetas_historial${q ? `?${q}` : ''}${separator}_t=${timestamp}`;
      const res = await fetch(url, { credentials: 'include' });
      const data = await res.json();
      const rows = Array.isArray(data) ? data : (data && data.value ? data.value : []);
      setResultadosTarjetas(rows || []);
    } catch (err) {
      console.error('Error fetching tarjetas historial:', err);
      setResultadosTarjetas([]);
    }
  };

  const fetchPersonasSinTarjeta = async (filtros = {}) => {
    setFiltrosPersonasSinTarjeta(filtros);
    const url = `/api/reportes/personas-registradas-sin-tarjeta`;
    try {
      const res = await fetch(url, { credentials: 'include' });
      const data = await res.json();
      const rows = Array.isArray(data) ? data : (data && data.value ? data.value : []);
      setResultadosPersonasSinTarjeta(rows || []);
    } catch (err) {
      console.error('Error fetching personas sin tarjeta:', err);
      setResultadosPersonasSinTarjeta([]);
    }
  };

  // Export helpers
  const exportAccesosExcel = (filtros = {}) => {
    const q = buildQuery(filtros);
    window.open(`/exportar_excel_accesos?${q}`, '_blank');
  };

  const exportAccesosPDF = (filtros = {}) => {
    const q = buildQuery(filtros);
    window.open(`/reporte_accesos_personal?${q}`, '_blank');
  };

  const exportTarjetasExcel = (filtros = {}) => {
    const q = buildQuery(filtros);
    window.open(`/exportar_excel_tarjetas?${q}`, '_blank');
  };

  const exportTarjetasPDF = (filtros = {}) => {
    const q = buildQuery(filtros);
    window.open(`/reporte_tarjetas?${q}`, '_blank');
  };

  let content = null;
  if (view === 'personas') content = <Personas onGoHome={() => setView('dashboard')} />;
  else if (view === 'usuarios') content = <Usuarios onGoHome={() => setView('dashboard')} />;
  else if (view === 'tarjetas') content = <TarjetasRegistradas onGoHome={() => setView('dashboard')} />;
  else if (view === 'enrolar') content = <Enrolar onGoHome={() => setView('dashboard')} />;
  else if (view === 'registro_tarjeta') content = <RegistroTarjeta onGoHome={() => setView('dashboard')} />;
  else if (view === 'tipo_movimiento') content = <TipoMovimiento onGoHome={() => setView('dashboard')} />;
  else if (view === 'tipo_registro') content = <TipoRegistro onGoHome={() => setView('dashboard')} />;
  else if (view === 'perfil_persona') content = <PerfilPersona onGoHome={() => setView('dashboard')} onNavigate={(v) => setView(v)} />;
  else if (view === 'bitacora') content = <BitacoraViewer onGoHome={() => setView('dashboard')} />;
  else if (view === 'reportes_ingresos') content = (
    <ReportesIngresos
      onGoHome={() => setView('dashboard')}
      onFiltrar={fetchTarjetas}
      resultados={resultadosTarjetas}
      filtros={filtrosTarjetas}
      onExportExcel={() => exportTarjetasExcel(filtrosTarjetas)}
      onExportPDF={() => exportTarjetasPDF(filtrosTarjetas)}
    />
  );
  else if (view === 'permisos') content = <Permisos onGoHome={() => setView('dashboard')} />;
  else if (view === 'roles') content = <Roles onGoHome={() => setView('dashboard')} />;
  else if (view === 'dispositivos') content = <Dispositivos onGoHome={() => setView('dashboard')} />;
  else if (view === 'accesos_historial') content = (
    <AccesosHistorial
      onVolver={() => setView('dashboard')}
      onFiltrar={fetchAccesos}
      resultados={resultadosAccesos}
      filtros={filtrosAccesos}
      onExportExcel={() => exportAccesosExcel(filtrosAccesos)}
      onExportPDF={() => exportAccesosPDF(filtrosAccesos)}
    />
  );
  else if (view === 'personas_registradas_sin_tarjeta') content = (
    <PersonasRegistradasSinTarjeta
      onVolver={() => setView('dashboard')}
      onFiltrar={fetchPersonasSinTarjeta}
      resultados={resultadosPersonasSinTarjeta}
      filtros={filtrosPersonasSinTarjeta}
      onExportExcel={() => exportAccesosExcel(filtrosPersonasSinTarjeta)}
      onExportPDF={() => exportAccesosPDF(filtrosPersonasSinTarjeta)}
    />
  );
  // The standalone "registro_persona_emergencia" view was removed from main navigation
  // to keep emergency contact registration available only inside person registration flows.
  else if (view === 'tarjetas_historial') content = (
    <TarjetasHistorial
      onVolver={() => setView('dashboard')}
      onFiltrar={fetchTarjetas}
      resultados={resultadosTarjetas}
      filtros={filtrosTarjetas}
      onExportExcel={() => exportTarjetasExcel(filtrosTarjetas)}
      onExportPDF={() => exportTarjetasPDF(filtrosTarjetas)}
    />
  );
  else {
    const todayStr = new Date().toLocaleDateString();
    content = (
      <div className="dashboard-page">
        <div className="dashboard-container container">
          <div className="dashboard-header">
            <div>
              <h2>Bienvenido, {usuario} 👋</h2>
              <div className="dashboard-subtitle">Hoy: {todayStr}</div>
            </div>
           
          </div>

          <div className="row mb-4">
            <div className="col-md-4">
              <StatCard title="Personas" value={loadingStats ? '...' : stats.personas} color="primary" onClick={() => setView('personas')} icon={<FaUser size={28} />} />
            </div>
            <div className="col-md-4">
              <StatCard title="Tarjetas" value={loadingStats ? '...' : stats.tarjetas} color="success" onClick={() => setView('tarjetas')} icon={<FaIdCard size={28} />} />
            </div>
            <div className="col-md-4">
              <StatCard title="Accesos" value={loadingStats ? '...' : stats.accesos} color="warning" onClick={() => { setView('accesos_historial'); fetchAccesos({}); }} icon={<FaDoorOpen size={28} />} />
            </div>
          </div>

          <div className="row">
            <div className="col-md-8">
              <div className="card mb-3">
                <div className="card-header">Últimos accesos</div>
                <div className="card-body">
                  {ultimosAccesos.length === 0 ? (
                    <p className="text-muted">No hay registros recientes.</p>
                  ) : (
                    <div className="table-responsive">
                      <table className="table table-sm">
                        <thead>
                          <tr>
                            <th>Fecha</th>
                            <th>Persona</th>
                            <th>Movimiento</th>
                            <th>Resultado</th>
                            <th>Credencial</th>
                          </tr>
                        </thead>
                        <tbody>
                          {ultimosAccesos.map((r, idx) => (
                            <tr key={idx}>
                              <td>{r.fecha_hora || r.fecha || '-'}</td>
                              <td>{r.persona || r.nombre || r.usuario_responsable || '-'}</td>
                              <td>{r.movimiento || r.accion || r.tipo || '-'}</td>
                              <td>{r.resultado || '-'}</td>
                              <td>{r.credencial || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="col-md-4">
              <div className="card mb-3">
                <div className="card-header">Últimas tarjetas</div>
                <div className="card-body">
                  {ultimosTarjetas.length === 0 ? (
                    <p className="text-muted">No hay tarjetas registradas.</p>
                  ) : (
                    <div className="list-group list-group-flush">
                      {ultimosTarjetas.map((t, i) => (
                        <div className="list-group-item" key={i}>
                          <div className="fw-bold">{t.nombre_completo || t.nombre || '—'}</div>
                          <small className="text-muted">{t.uid || t.codigo || '-'}</small>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="d-grid mt-3">
                    <button className="btn btn-primary" onClick={() => { setView('tarjetas_historial'); fetchTarjetas({}); }}>
                      Ver historial completo
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    );
  }

  return (
    <div className="app-shell d-flex flex-column">
      <TopNav usuario={usuario} onLogout={onLogout} onNavigate={(v) => setView(v)} />
      <main className="app-main p-3 flex-grow-1 container mt-3">
        {content}
      </main>
    </div>
  );
}
