import React, { useEffect, useState } from 'react';

export default function BitacoraViewer({ onGoHome }) {
  const [rows, setRows] = useState([]);
  const [modulo, setModulo] = useState('');
  const [accion, setAccion] = useState('');
  const [usuario, setUsuario] = useState('');
  const [page, setPage] = useState(1);
  const limit = 25;

  const load = async () => {
    const params = new URLSearchParams();
    if (modulo) params.append('modulo', modulo);
    if (accion) params.append('accion', accion);
    if (usuario) params.append('usuario', usuario);
    params.append('limit', String(limit));
    const res = await fetch('/api/bitacora?' + params.toString(), { credentials: 'include' });
    const data = await res.json();
    setRows(Array.isArray(data) ? data : []);
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="card">
      <div className="card-header">Bitácora</div>
      <div className="card-body">
        <div className="row mb-3">
          <div className="col-md-3"><input className="form-control" placeholder="Módulo" value={modulo} onChange={e => setModulo(e.target.value)} /></div>
          <div className="col-md-3"><input className="form-control" placeholder="Acción" value={accion} onChange={e => setAccion(e.target.value)} /></div>
          <div className="col-md-3"><input className="form-control" placeholder="Usuario" value={usuario} onChange={e => setUsuario(e.target.value)} /></div>
          <div className="col-md-3 d-flex gap-2"><button className="btn btn-primary" onClick={() => { setPage(1); load(); }}>Filtrar</button><button className="btn btn-secondary" onClick={() => { setModulo(''); setAccion(''); setUsuario(''); setPage(1); load(); }}>Limpiar</button></div>
        </div>
        {rows.length === 0 ? <p className="text-muted">Sin registros</p> : (
          <div className="table-responsive"><table className="table"><thead><tr><th>Fecha</th><th>Módulo</th><th>Acción</th><th>Usuario</th><th>Descripción</th></tr></thead><tbody>{rows.slice((page-1)*limit, page*limit).map((r,i)=>(<tr key={i}><td>{r.fecha_hora}</td><td>{r.modulo}</td><td>{r.accion}</td><td>{r.usuario}</td><td>{r.descripcion}</td></tr>))}</tbody></table></div>
        )}
        <div className="d-flex justify-content-between align-items-center mt-3">
          <div>
            <button className="btn btn-secondary me-2" onClick={() => { if (page>1) setPage(page-1); }}>{'<'}</button>
            <button className="btn btn-secondary" onClick={() => { setPage(page+1); }}>{'>'}</button>
          </div>
          <div><button className="btn btn-secondary" onClick={onGoHome}>Volver</button></div>
        </div>
      </div>
    </div>
  );
}
