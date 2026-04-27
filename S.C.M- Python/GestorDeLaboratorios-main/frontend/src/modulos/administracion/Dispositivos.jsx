import React, { useEffect, useState, useRef } from 'react'

export default function Dispositivos() {
  const [dispositivos, setDispositivos] = useState([])
  const [nombre, setNombre] = useState('')
  const [apikey, setApikey] = useState('')
  const [loading, setLoading] = useState(false)
  const [creating, setCreating] = useState(false)
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)
  const timeoutRef = useRef(null)

  const clearMessages = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    timeoutRef.current = setTimeout(()=>{ setMessage(null); setError(null) }, 4500)
  }

  const fetchList = async () => {
    setLoading(true)
    try {
      const r = await fetch('/api/dispositivos')
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      const data = await r.json()
      setDispositivos(Array.isArray(data) ? data : (data.value || []))
    } catch (err) {
      setError('Error al cargar dispositivos: ' + (err.message || err))
      clearMessages()
    } finally {
      setLoading(false)
    }
  }

  useEffect(()=>{ fetchList() }, [])

  const create = async () => {
    if (!nombre || !apikey) {
      setError('Nombre y ApiKey son requeridos')
      clearMessages()
      return
    }
    setCreating(true)
    try {
      const r = await fetch('/api/dispositivos', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ nombre, apikey }) })
      const data = await r.json()
      if (!r.ok) throw new Error(data && data.error ? data.error : `HTTP ${r.status}`)
      setMessage('Dispositivo creado correctamente')
      setNombre(''); setApikey('')
      fetchList()
    } catch (err) {
      setError('No se pudo crear el dispositivo: ' + (err.message || err))
    } finally {
      setCreating(false)
      clearMessages()
    }
  }

  const toggle = async (id, active, nombre) => {
    const ok = window.confirm(`${active ? 'Desactivar' : 'Activar'} dispositivo "${nombre}"?`)
    if (!ok) return
    try {
      const path = active ? 'desactivar' : 'activar'
      const r = await fetch(`/api/dispositivos/${id}/${path}`, { method: 'PUT' })
      if (!r.ok) {
        const txt = await r.text()
        throw new Error(txt || `HTTP ${r.status}`)
      }
      setMessage(`Dispositivo ${active ? 'desactivado' : 'activado'} correctamente`)
      fetchList()
    } catch (err) {
      setError('Error al actualizar: ' + (err.message || err))
    } finally {
      clearMessages()
    }
  }

  return (
    <div>
      <h2>Dispositivos</h2>

      {message && <div className="alert alert-success" role="alert">{message}</div>}
      {error && <div className="alert alert-danger" role="alert">{error}</div>}

      <div style={{marginBottom:12, display:'flex', gap:8}}>
        <input placeholder="Nombre" value={nombre} onChange={e=>setNombre(e.target.value)} />
        <input placeholder="ApiKey" value={apikey} onChange={e=>setApikey(e.target.value)} />
        <button className="btn btn-primary" onClick={create} disabled={creating}>{creating ? 'Creando...' : 'Crear'}</button>
        <button className="btn btn-secondary" onClick={fetchList} disabled={loading}>{loading ? 'Cargando...' : 'Refrescar'}</button>
      </div>

      <div className="table-responsive">
      <table className="table table-sm">
        <thead><tr><th>ID</th><th>Nombre</th><th>ApiKey</th><th>Activo</th><th>Acciones</th></tr></thead>
        <tbody>
          {dispositivos.map(d=> (
                <tr key={d.id || d.IdDispositivo}>
                  <td>{d.id || d.IdDispositivo}</td>
                  <td>{d.nombre || d.Nombre}</td>
                  <td><code style={{fontSize:12}}>{d.api_key || d.ApiKey}</code></td>
                  <td>{(typeof d.activo !== 'undefined' ? d.activo : d.Activo) ? 'Sí' : 'No'}</td>
                  <td>
                    <button className="btn btn-sm btn-outline-primary" onClick={()=>toggle(d.id || d.IdDispositivo, (typeof d.activo !== 'undefined' ? d.activo : d.Activo), (d.nombre || d.Nombre))}>
                      {(typeof d.activo !== 'undefined' ? d.activo : d.Activo) ? 'Desactivar' : 'Activar'}
                    </button>
                  </td>
                </tr>
              ))}
          {dispositivos.length === 0 && !loading && (
            <tr><td colSpan={5} className="text-muted">No hay dispositivos registrados.</td></tr>
          )}
        </tbody>
      </table>
      </div>
    </div>
  )
}
