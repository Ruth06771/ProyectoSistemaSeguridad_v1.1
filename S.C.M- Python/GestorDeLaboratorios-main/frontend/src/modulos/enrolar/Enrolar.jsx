import React, { useState, useEffect, useRef } from 'react';

export default function Enrolar({ onGoHome }) {
  const [persona, setPersona] = useState({ nombre_completo: '', correo: '', tipo_sangre: '' });
  const [personasList, setPersonasList] = useState([]);
  const searchTimer = useRef(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const [tarjetasList, setTarjetasList] = useState([]);
  const [useManualUid, setUseManualUid] = useState(false);
  const [tarjeta, setTarjeta] = useState({ uid: '', nombre_completo: '', correo: '', pin: '' });
  const [tarjetaQuery, setTarjetaQuery] = useState('');
  const [tarjetaSuggestions, setTarjetaSuggestions] = useState([]);
  const [showTarjetaSuggestions, setShowTarjetaSuggestions] = useState(false);
  const tarjetaRef = useRef(null);
  const [perfil, setPerfil] = useState({ nombre: '', perfil_acceso_lab_id: '' });
  const [perfilesList, setPerfilesList] = useState([]);
  const [showPerfiles, setShowPerfiles] = useState(false);
  const [msg, setMsg] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedPreview, setSelectedPreview] = useState(null);
  const [enrolarList, setEnrolarList] = useState([]);
  const [selectedEnrolar, setSelectedEnrolar] = useState(null);
  const [tableLoading, setTableLoading] = useState(false);

  const resetForm = () => {
    setPersona({ nombre_completo: '', correo: '', tipo_sangre: '', documento_identidad: '' });
    setSearchQuery('');
    setSuggestions([]);
    setShowSuggestions(false);
    setShowAll(false);
    setSelectedPreview(null);
    setTarjeta({ uid: '', nombre_completo: '', correo: '', pin: '' });
    setTarjetaQuery('');
    setPerfil({ nombre: '', perfil_acceso_lab_id: '' });
    setSelectedEnrolar(null);
  };

  const loadEnrolarList = async () => {
    console.log('[loadEnrolarList] Starting to load enrolar list...');
    setTableLoading(true);
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // Timeout de 10 segundos
      
      const res = await fetch('/api/enrolar', { 
        credentials: 'include', 
        cache: 'no-store',
        headers: { 'Cache-Control': 'no-cache, no-store, must-revalidate' },
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      if (!res.ok) {
        console.error('Error cargando lista de enrolados', res.status, res.statusText);
        setEnrolarList([]);
        return;
      }
      const data = await res.json();
      console.log('[loadEnrolarList] Fetched data:', data);
      const list = Array.isArray(data)
        ? data
        : Array.isArray(data?.data)
          ? data.data
          : [];
      console.log('[loadEnrolarList] Parsed list, length:', list.length);
      if (list.length > 0) {
        console.log('[loadEnrolarList] First row:', list[0]);
      }
      setEnrolarList(list);
    } catch (err) {
      console.error('Error cargando lista de enrolados', err);
      if (err.name === 'AbortError') {
        setMsg('⚠ La carga de la lista tardó demasiado. Intenta nuevamente.');
      }
      setEnrolarList([]);
    } finally {
      setTableLoading(false);
      console.log('[loadEnrolarList] Table loading state set to false');
    }
  };

  const handleCancelEdit = () => {
    resetForm();
    setMsg('Edición cancelada');
  };

  const handleEditEnrolar = (row) => {
    setSelectedEnrolar(row);
    setPersona({ 
      nombre_completo: row.nombre_completo || '', 
      correo: row.correo || '', 
      tipo_sangre: row.tipo_sangre || '', 
      documento_identidad: row.documento_identidad || '',
      id: row.persona_id 
    });
    setSearchQuery(row.nombre_completo || '');
    setSelectedPreview({ 
      nombre_completo: row.nombre_completo || '', 
      correo: row.correo || '', 
      documento_identidad: row.documento_identidad || '', 
      tipo_sangre: row.tipo_sangre || '' 
    });
    setTarjeta({ uid: row.tarjeta_uid || '', nombre_completo: row.nombre_completo || '', correo: row.correo || '', pin: row.pin || '' });
    setTarjetaQuery(row.tarjeta_uid || '');
    const perfilName = row.perfil || (perfilesList.find((pf) => String(pf.id) === String(row.perfil_id))?.nombre || '');
    setPerfil({ nombre: perfilName, perfil_acceso_lab_id: row.perfil_id });
    setMsg(`Editando enrolamiento #${row.id}`);
  };

  const handleUpdateEnrolarAction = async (row, accion, estado = undefined) => {
    try {
      const body = { accion };
      if (estado !== undefined) {
        body.estado = estado;
      }
      const res = await fetch(`/api/enrolar/${row.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        credentials: 'include'
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setMsg(`Acción '${accion}' aplicada correctamente.`);
        await loadEnrolarList();
      } else {
        setMsg(data.error || data.message || 'Error al aplicar acción');
      }
    } catch (err) {
      setMsg('Error de conexión al aplicar acción');
      console.error(err);
    }
  };

  const handleDeleteEnrolar = async (row) => {
    if (!window.confirm('¿Eliminar este enrolamiento? Esta acción no se puede deshacer.')) return;
    try {
      const res = await fetch(`/api/enrolar/${row.id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setMsg('Enrolamiento eliminado correctamente.');
        if (selectedEnrolar && selectedEnrolar.id === row.id) {
          resetForm();
        }
        await loadEnrolarList();
      } else {
        setMsg(data.error || data.message || 'Error al eliminar enrolamiento');
      }
    } catch (err) {
      setMsg('Error de conexión al eliminar enrolamiento');
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // client-side validation
    if (!persona.nombre_completo || persona.nombre_completo.trim() === '') { setMsg('Nombre de persona es requerido'); return; }
    if (!tarjeta.uid || tarjeta.uid.trim() === '') { setMsg('UID de tarjeta es requerido'); return; }
    if (!perfil || !perfil.perfil_acceso_lab_id) { setMsg('Perfil es requerido'); return; }
    setMsg('Enrolando...'); 
    setLoading(true);
    try {
      const url = selectedEnrolar ? `/api/enrolar/${selectedEnrolar.id}` : '/api/enrolar';
      const method = selectedEnrolar ? 'PUT' : 'POST';
      const body = { persona, tarjeta, perfil: { perfil_acceso_lab_id: perfil.perfil_acceso_lab_id, nombre: perfil.nombre } };
      if (selectedEnrolar) {
        body.estado = selectedEnrolar.estado;
        body.accion = 'editado';
      }
      console.log(`[handleSubmit] Sending ${method} to ${url}`, body);
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        credentials: 'include',
        cache: 'no-store'
      });
      console.log(`[handleSubmit] Response status: ${res.status}`);
      const j = await res.json();
      console.log('[handleSubmit] Response data:', j);
      
      if (res.ok && j.success) {
        if (selectedEnrolar) {
          setMsg('✓ Enrolamiento actualizado correctamente.');
          console.log('[handleSubmit] PUT successful, updating local list...');
          const updatedRow = {
            ...selectedEnrolar,
            nombre_completo: persona.nombre_completo || selectedEnrolar.nombre_completo,
            correo: persona.correo || selectedEnrolar.correo,
            documento_identidad: persona.documento_identidad || selectedEnrolar.documento_identidad,
            tipo_sangre: persona.tipo_sangre || selectedEnrolar.tipo_sangre,
            tarjeta_uid: tarjeta.uid || selectedEnrolar.tarjeta_uid,
            pin: tarjeta.pin || selectedEnrolar.pin,
            perfil: perfil.nombre || selectedEnrolar.perfil,
            perfil_id: perfil.perfil_acceso_lab_id || selectedEnrolar.perfil_id,
            estado: selectedEnrolar.estado ?? 1,
            accion: selectedEnrolar.accion || 'editado'
          };
          setEnrolarList(prev => prev.map((row) => (row.id === selectedEnrolar.id ? updatedRow : row)));
          await new Promise(resolve => setTimeout(resolve, 500));
          try {
            await loadEnrolarList();
            console.log('[handleSubmit] List reloaded after edit');
          } catch (e) {
            console.error('[handleSubmit] Error reloading list:', e);
          }
        } else {
          // POST - nuevo enrolamiento
          setMsg('✓ Enrolado correctamente.');
          console.log('[handleSubmit] POST successful, adding to list...');
          const newRow = {
            id: j.enrolar_id || null,
            persona_id: j.persona_id || null,
            tarjeta_id: j.tarjeta_id || null,
            tarjeta_uid: tarjeta.uid || '-',
            pin: tarjeta.pin || '-',
            perfil: perfil.nombre || '-',
            perfil_id: perfil.perfil_acceso_lab_id,
            estado: 1,
            accion: 'activo',
            fecha_de_registro: new Date().toISOString().slice(0, 19).replace('T', ' '),
            nombre_completo: persona.nombre_completo || '-',
            correo: persona.correo || '-',
            documento_identidad: persona.documento_identidad || '-',
            tipo_sangre: persona.tipo_sangre || '-'
          };
          setEnrolarList(prev => [newRow, ...prev]);
          // Para POST, no hacemos loadEnrolarList() ya que acabamos de agregar
          console.log('[handleSubmit] New row added to table');
        }
        resetForm();
      } else {
        const errorMsg = j.message || j.error || 'Error desconocido';
        setMsg(`✗ Error: ${errorMsg}`);
        console.error('[handleSubmit] API returned error:', j);
      }
    } catch (err) {
      setMsg(`✗ Error de conexión: ${err.message}`);
      console.error('[handleSubmit] Caught exception:', err);
    } finally {
      setLoading(false);
      console.log('[handleSubmit] Loading state set to false');
    }
  };

  useEffect(() => {
    // Load personas once for local search/autocomplete
    const load = async () => {
      try {
        const res = await fetch('/api/personas', { credentials: 'include' });
        const data = await res.json();
        setPersonasList(data || []);
      } catch (err) {
        console.error('No se pudo cargar la lista de personas', err);
      }
    };
    load();
    // Load tarjetas so Enrolar can pick existing registered cards
    const loadTarjetas = async () => {
      try {
        const r = await fetch('/api/tarjetas', { credentials: 'include' });
        const t = await r.json();
        setTarjetasList(t || []);
      } catch (err) {
        console.error('No se pudo cargar tarjetas', err);
      }
    };
    const loadPerfiles = async () => {
      try {
        const r = await fetch('/api/perfil_acceso_lab', { credentials: 'include' });
        if (r.ok) {
          const p = await r.json();
          setPerfilesList(Array.isArray(p) ? p : []);
        }
      } catch (err) {
        console.error('No se pudo cargar perfiles de acceso', err);
      }
    };
    const loadAll = async () => {
      await load();
      await loadTarjetas();
      await loadPerfiles();
      await loadEnrolarList();
    };
    loadAll();
  }, []);

  useEffect(() => {
    const onDocClick = (ev) => {
      if (tarjetaRef.current && !tarjetaRef.current.contains(ev.target)) {
        setShowTarjetaSuggestions(false);
      }
    };
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  // Deprecated typed search; we now show full dropdown when requested
  const onSearchChange = (q) => {
    setSearchQuery(q);
    // debounce remote search
    if (searchTimer.current) clearTimeout(searchTimer.current);
    if (!q || q.trim() === '') {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    searchTimer.current = setTimeout(async () => {
      try {
        const res = await fetch(`/api/personas/search_with_tarjeta?q=${encodeURIComponent(q)}`, { credentials: 'include' });
        if (!res.ok) {
          setSuggestions([]);
          setShowSuggestions(false);
          return;
        }
        const data = await res.json();
        setSuggestions(data || []);
        setShowSuggestions(true);
      } catch (err) {
        console.error('Error buscando personas', err);
        setSuggestions([]);
        setShowSuggestions(false);
      }
    }, 300);
  };

  const getBloodBadgeClass = (tipo) => {
    if (!tipo) return 'badge bg-secondary';
    const t = tipo.toUpperCase();
    if (t.startsWith('A')) return 'badge bg-danger';
    if (t.startsWith('B')) return 'badge bg-warning text-dark';
    if (t.startsWith('AB')) return 'badge bg-info text-dark';
    if (t.startsWith('O')) return 'badge bg-success';
    return 'badge bg-secondary';
  };

  const selectPersona = (p) => {
    setPersona({ 
      nombre_completo: p.nombre_completo || p.nombre || '', 
      correo: p.correo || '', 
      tipo_sangre: p.tipo_sangre || '', 
      documento_identidad: p.documento_identidad || '',
      id: p.id 
    });
    setSearchQuery(p.nombre_completo || p.nombre || '');
    setShowSuggestions(false);
    setShowAll(false);
    setSelectedPreview(p);
    // Try to find a tarjeta locally first
    const foundLocal = (tarjetasList || []).find(t => {
      if (!t) return false;
      const tname = (t.nombre_completo || t.nombre || '').toString().trim().toLowerCase();
      const pname = (p.nombre_completo || p.nombre || '').toString().trim().toLowerCase();
      const correoMatch = (t.correo || '').toString().toLowerCase() === ((p.correo || '').toString().toLowerCase());
      return (tname && pname && tname === pname) || correoMatch;
    });
    if (foundLocal) {
      setTarjeta({ uid: foundLocal.uid, nombre_completo: foundLocal.nombre_completo || '', correo: foundLocal.correo || '', pin: foundLocal.pin || '' });
      setTarjetaQuery(foundLocal.uid);
      return;
    }
    // If not found locally, query backend endpoint
    (async () => {
      try {
        const q = encodeURIComponent(p.nombre_completo || p.nombre || p.correo || '');
        const res = await fetch(`/api/tarjetas/search_by_persona?q=${q}`, { credentials: 'include' });
        if (!res.ok) return;
        const data = await res.json();
        if (data && data.length > 0) {
          const t = data[0];
          setTarjeta({ uid: t.uid, nombre_completo: t.nombre_completo || '', correo: t.correo || '', pin: t.pin || '' });
          setTarjetaQuery(t.uid);
        } else {
          // no tarjeta found; clear tarjeta fields so user can enter UID manually
          setTarjeta({ uid: '', nombre_completo: '', correo: '', pin: '' });
          setTarjetaQuery('');
        }
      } catch (err) {
        console.error('Error buscando tarjeta por persona', err);
      }
    })();
  };

  const onTarjetaSearch = (q) => {
    setTarjetaQuery(q);
    if (!q || q.trim() === '') {
      setTarjetaSuggestions([]);
      setShowTarjetaSuggestions(false);
      return;
    }
    const low = q.toLowerCase();
    const matches = tarjetasList.filter(t => (t.uid || '').toLowerCase().includes(low));
    setTarjetaSuggestions(matches.slice(0, 10));
    setShowTarjetaSuggestions(true);
  };

  const selectTarjeta = (t) => {
    setTarjeta({ uid: t.uid, nombre_completo: t.nombre_completo || t.nombre || '', correo: t.correo || '', pin: t.pin || '' });
    setTarjetaQuery(t.uid);
    setShowTarjetaSuggestions(false);
  };

  const clearSelection = () => {
    setPersona({ nombre_completo: '', correo: '', tipo_sangre: '' });
    setSearchQuery('');
    setSuggestions([]);
    setShowSuggestions(false);
    setShowAll(false);
    setSelectedPreview(null);
  };

  return (
    <div className="card">
      <div className="card-header">Enrolar persona</div>
      <div className="card-body">
  <form onSubmit={handleSubmit}>
        <div className="row">
          <div className="col-md-7">
          <h5 className="mb-3">Datos de persona</h5>
          <div className="mb-2">
            <div className="d-flex align-items-center gap-2">
              <button type="button" className="btn btn-outline-secondary" onClick={() => setShowAll(!showAll)}>
                {showAll ? 'Cerrar lista' : `Abrir lista desplegable (${personasList.length})`}
              </button>
              <button type="button" className="btn btn-sm btn-link" onClick={clearSelection}>Limpiar selección</button>
            </div>
            {showAll && (
              <div className="mt-1" style={{ zIndex: 1000 }}>
                <div className="mb-2">
                  <input
                    className="form-control"
                    placeholder="Buscar persona por nombre o correo..."
                    value={searchQuery}
                    onChange={e => onSearchChange(e.target.value)}
                    onFocus={() => { if (searchQuery) setShowSuggestions(true); }}
                  />
                  {showSuggestions && (
                    <div className="list-group position-relative" style={{ width: '100%', maxHeight: 220, overflowY: 'auto' }}>
                      {suggestions.length === 0 ? (
                        <div className="list-group-item text-muted small">Sin resultados</div>
                      ) : (
                        suggestions.map((s, idx) => (
                          <button key={`sugg-${s.id}-${idx}`} type="button" className="list-group-item list-group-item-action" onClick={() => { selectPersona(s); setShowSuggestions(false); }}>
                            <div><strong>{s.nombre_completo || s.nombre}</strong> <small className="text-muted">#{s.id}</small></div>
                            <div className="small text-muted">{s.correo || ''} {s.documento_identidad ? ` • ${s.documento_identidad}` : ''}</div>
                          </button>
                        ))
                      )}
                    </div>
                  )}
                </div>

                <div className="list-group" style={{ maxHeight: '320px', overflowY: 'auto' }}>
                  {personasList.length === 0 ? (
                    <div className="list-group-item text-muted small">No hay personas</div>
                  ) : (
                    personasList.map((s, idx) => {
                      const active = selectedPreview && selectedPreview.id === s.id;
                      return (
                        <button
                          type="button"
                          key={`${s.id}-${idx}`}
                          className={`list-group-item list-group-item-action d-flex align-items-center ${active ? 'active' : ''}`}
                          onClick={() => { selectPersona(s); }}
                          style={{ padding: '10px 12px' }}
                        >
                          <div style={{ width: 48, height: 48, borderRadius: 24, background: active ? '#0d6efd' : '#e9ecef', color: active ? 'white' : 'black', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, marginRight: 12 }}>
                            {((s.nombre_completo || s.nombre || '')
                              .split(' ')
                              .filter(Boolean)
                              .map(x => x[0])
                              .slice(0,2)
                              .join('') || '?')}
                          </div>
                          <div style={{ flex: 1 }}>
                            <div className="d-flex align-items-start justify-content-between">
                              <div>
                                <div style={{ fontSize: 14 }}><strong>{s.nombre_completo || s.nombre}</strong> <small className="text-muted ms-2">#{s.id}</small></div>
                                <div className="small text-muted mt-1">{s.documento_identidad ? `Doc: ${s.documento_identidad}` : ''} {s.correo ? ` • ${s.correo}` : ''}</div>
                              </div>
                              <div className="text-end">
                                {s.tipo_sangre && <span className={`${getBloodBadgeClass(s.tipo_sangre)} ms-2`}>{s.tipo_sangre}</span>}
                              </div>
                            </div>
                          </div>
                        </button>
                      );
                    })
                  )}
                </div>
              </div>
            )}
            {/* Search input for large lists: autocomplete suggestions */}
            <div className="mt-2 position-relative">
              <input
                className="form-control"
                placeholder="Buscar persona por nombre o correo..."
                value={searchQuery}
                onChange={e => onSearchChange(e.target.value)}
                onFocus={() => { if (searchQuery) setShowSuggestions(true); }}
              />
              {showSuggestions && (
                <div className="list-group position-absolute" style={{ zIndex: 1100, width: '100%', maxHeight: 220, overflowY: 'auto' }}>
                  {suggestions.length === 0 ? (
                    <div className="list-group-item text-muted small">Sin resultados</div>
                  ) : (
                    suggestions.map((s, idx) => (
                      <button key={`sugg-${s.id}-${idx}`} type="button" className="list-group-item list-group-item-action" onClick={() => { selectPersona(s); setShowSuggestions(false); }}>
                        <div><strong>{s.nombre_completo || s.nombre}</strong> <small className="text-muted">#{s.id}</small></div>
                        <div className="small text-muted">{s.correo || ''} {s.documento_identidad ? ` • ${s.documento_identidad}` : ''}</div>
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
            {/* Removed duplicate editable 'Nombre completo' field: search input above fills persona directly */}
          <div className="mb-2">
            <input className="form-control" placeholder="Correo" value={persona.correo} onChange={e => setPersona({...persona, correo: e.target.value})} />
          </div>
          <div className="mb-2">
            <input className="form-control" placeholder="Documento de identidad (Carnet)" value={persona.documento_identidad} onChange={e => setPersona({...persona, documento_identidad: e.target.value})} />
          </div>
          <div className="mb-2">
            <select className="form-select" value={persona.tipo_sangre || ''} onChange={e => setPersona({...persona, tipo_sangre: e.target.value})}>
              <option value="">Tipo de sangre...</option>
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

          <h5 className="mt-4">Tarjeta</h5>
          <div className="mb-2" ref={tarjetaRef}>
            <div className="d-flex gap-2 align-items-center">
              <input
                className="form-control"
                placeholder="UID o parte del UID (escribe para buscar)"
                value={useManualUid ? (tarjeta.uid || '') : (tarjetaQuery || '')}
                onChange={e => {
                  const v = e.target.value;
                  if (useManualUid) {
                    setTarjeta({ ...tarjeta, uid: v });
                    setTarjetaQuery(v);
                  } else {
                    setTarjetaQuery(v);
                    onTarjetaSearch(v);
                  }
                }}
                onFocus={() => { if (!useManualUid && tarjetaQuery) setShowTarjetaSuggestions(true); }}
              />
              <div className="form-check ms-2">
                <input id="manualUid" className="form-check-input" type="checkbox" checked={useManualUid} onChange={e => setUseManualUid(e.target.checked)} />
                <label className="form-check-label" htmlFor="manualUid">Ingresar UID manualmente</label>
              </div>
            </div>

            {!useManualUid && showTarjetaSuggestions && (
              <div className="list-group mt-1" style={{ maxHeight: '200px', overflowY: 'auto' }}>
                {tarjetaSuggestions.length === 0 ? (
                  <div className="list-group-item text-muted small">Sin coincidencias</div>
                ) : (
                  tarjetaSuggestions.map(t => (
                    <button type="button" key={t.id || t.uid} className="list-group-item list-group-item-action" onClick={() => { selectTarjeta(t); setShowTarjetaSuggestions(false); }}>
                      <div><strong>{t.uid}</strong> <small className="text-muted">{t.nombre_completo || ''}</small></div>
                      <div className="small text-muted">{t.correo || ''}</div>
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
          <div className="mb-2">
            
            <h5>PIN</h5>
            <input className="form-control" placeholder="PIN" value={tarjeta.pin || ''} readOnly />
          </div>

          <h5>Perfil</h5>
          <div className="mb-2">
            <div className="d-flex align-items-center gap-2">
              <button type="button" className="btn btn-outline-secondary" onClick={() => setShowPerfiles(!showPerfiles)}>
                {showPerfiles ? 'Cerrar perfiles' : `Seleccionar perfil (${perfilesList.length})`}
              </button>
              <button type="button" className="btn btn-sm btn-link" onClick={() => setPerfil({ nombre: '', perfil_acceso_lab_id: '' })}>Limpiar perfil</button>
            </div>
            {showPerfiles && (
              <div className="list-group mt-1" style={{ maxHeight: '260px', overflowY: 'auto', zIndex: 1000 }}>
                {(perfilesList.length > 0 ? perfilesList : [
                  { id: 'estudiante', nombre: 'Estudiante' },
                  { id: 'docente', nombre: 'Docente' },
                  { id: 'auxiliar', nombre: 'Auxiliar' },
                  { id: 'admin', nombre: 'Administrador' }
                ]).map((pf) => {
                  const isSelected = perfil && (String(perfil.perfil_acceso_lab_id) === String(pf.id) || perfil.nombre === pf.nombre);
                  return (
                    <button key={pf.id} type="button" className={`list-group-item list-group-item-action d-flex justify-content-between align-items-center ${isSelected ? 'active' : ''}`} onClick={() => { setPerfil({ nombre: pf.nombre, perfil_acceso_lab_id: pf.id }); setShowPerfiles(false); }}>
                      <div>
                        <strong>{pf.nombre}</strong>
                        <div className="small text-muted">Role key: {pf.id}</div>
                      </div>
                      <div>
                        {isSelected ? <span className="badge bg-success">✓ Seleccionado</span> : <span className="badge bg-secondary">Perfil</span>}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
            {perfil && perfil.nombre && (
              <div className="mt-2">
                <div><strong>Perfil seleccionado:</strong> {perfil.nombre} {perfil.perfil_acceso_lab_id ? <small className="text-muted">(key: {perfil.perfil_acceso_lab_id})</small> : null}</div>
              </div>
            )}
          </div>
          </div>{/* end left column */}
          <div className="col-md-5">
            <div className="card border-0 shadow-sm">
              <div className="card-body text-center">
                <div style={{ width: 96, height: 96, borderRadius: 48, background: '#f1f5f9', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 28, fontWeight: 800, marginBottom: 12 }}>
                  {selectedPreview ? ((selectedPreview.nombre_completo || selectedPreview.nombre || '').split(' ').filter(Boolean).map(x => x[0]).slice(0,2).join('')) : '?'}
                </div>
                <h5 className="card-title mb-0">{selectedPreview ? (selectedPreview.nombre_completo || selectedPreview.nombre) : (persona.nombre_completo || 'Sin selección')}</h5>
                <div className="small text-muted mb-2">{selectedPreview ? `#${selectedPreview.id}` : ''}</div>
                {selectedPreview && selectedPreview.tipo_sangre && (
                  <div className="mb-2"><span className={`${getBloodBadgeClass(selectedPreview.tipo_sangre)}`}>{selectedPreview.tipo_sangre}</span></div>
                )}
                <div className="text-start">
                  <div><strong>Documento:</strong> {selectedPreview ? (selectedPreview.documento_identidad || '—') : (persona.documento_identidad || '—')}</div>
                  <div><strong>Correo:</strong> {selectedPreview ? (selectedPreview.correo || '—') : (persona.correo || '—')}</div>
                  <div><strong>Tarjeta UID:</strong> {tarjeta.uid || '—'}</div>
                  <div><strong>Perfil:</strong> {perfil && perfil.nombre ? perfil.nombre : '—'}</div>
                </div>
                <div className="mt-3">
                  <button className="btn btn-lg btn-success me-2" type="submit" style={{ backgroundImage: 'linear-gradient(90deg,#16a34a,#10b981)', border: 'none' }}>{loading ? (selectedEnrolar ? 'Guardando...' : 'Enrolando...') : (selectedEnrolar ? 'Guardar cambios' : 'Enrolar ahora')}</button>
                  {selectedEnrolar && (
                    <button type="button" className="btn btn-lg btn-secondary" onClick={handleCancelEdit} disabled={loading}>
                      Cancelar edición
                    </button>
                  )}
                </div>
              </div>
            </div>
            <div className="mt-3 text-center">
              <button type="button" className="btn btn-outline-secondary" onClick={onGoHome}>Volver al inicio</button>
            </div>
          </div>{/* end right column */}
        </div>{/* end row */}
        </form>
        {msg && <div className="alert alert-info mt-3">{msg}</div>}

        <div className="mt-4">
          <div className="d-flex align-items-center justify-content-between mb-3">
            <div>
              <h5 className="mb-0">Personas enroladas</h5>
              <small className="text-muted">Mostrando {enrolarList.length} registro{enrolarList.length === 1 ? '' : 's'}</small>
            </div>
            <button type="button" className="btn btn-outline-secondary btn-sm" onClick={loadEnrolarList} disabled={tableLoading}>
              {tableLoading ? 'Cargando...' : 'Actualizar lista'}
            </button>
          </div>
          <div className="table-responsive">
            <table className="table table-sm table-bordered table-striped align-middle">
              <thead className="table-dark">
                <tr>
                  <th>ID</th>
                  <th>Persona</th>
                  <th>Correo</th>
                  <th>Documento</th>
                  <th>Tipo sangre</th>
                  <th>Tarjeta UID</th>
                  <th>PIN</th>
                  <th>Perfil</th>
                  <th>Estado</th>
                  <th>Acción actual</th>
                  <th>Fecha registro</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {enrolarList.length > 0 ? enrolarList.map((row) => (
                  <tr key={row.id}>
                    <td>{row.id}</td>
                    <td>{row.nombre_completo || '-'}</td>
                    <td>{row.correo || '-'}</td>
                    <td>{row.documento_identidad || '-'}</td>
                    <td>{row.tipo_sangre || '-'}</td>
                    <td>{row.tarjeta_uid || '-'}</td>
                    <td>{row.pin || '-'}</td>
                    <td>{row.perfil || '-'}</td>
                    <td>{row.estado === 1 || row.estado === '1' ? 'Activo' : 'Inactivo'}</td>
                    <td>{row.accion || '-'}</td>
                    <td>{row.fecha_de_registro || '-'}</td>
                    <td>
                      <div className="d-flex gap-1 flex-wrap">
                        <button type="button" className="btn btn-sm btn-success" onClick={() => handleUpdateEnrolarAction(row, 'activo', 1)}>
                          Activo
                        </button>
                        <button type="button" className="btn btn-sm btn-warning" onClick={() => handleUpdateEnrolarAction(row, 'inactivo', 0)}>
                          Inactivo
                        </button>
                        <button type="button" className="btn btn-sm btn-primary" onClick={() => handleEditEnrolar(row)}>
                          Editar
                        </button>
                        <button type="button" className="btn btn-sm btn-danger" onClick={() => handleDeleteEnrolar(row)}>
                          Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={11} className="text-center text-muted">
                      No hay enrolamientos registrados aún.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
