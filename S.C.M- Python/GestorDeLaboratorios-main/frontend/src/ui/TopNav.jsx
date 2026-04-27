import React, { useState, useRef, useEffect } from 'react';
import './topnav.css';

export default function TopNav({ usuario, onLogout, onNavigate }) {
  const [open, setOpen] = useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const rootRef = useRef(null);

  const toggle = (key) => setOpen((prev) => (prev === key ? null : key));

  // Close when clicking outside or when Escape pressed
  useEffect(() => {
    function onDocClick(e) {
      if (!rootRef.current) return;
      if (!rootRef.current.contains(e.target)) setOpen(null);
    }
    function onKey(e) {
      if (e.key === 'Escape') setOpen(null);
    }
    document.addEventListener('mousedown', onDocClick);
    document.addEventListener('touchstart', onDocClick);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDocClick);
      document.removeEventListener('touchstart', onDocClick);
      document.removeEventListener('keydown', onKey);
    };
  }, []);

  // Helper to open and focus first submenu item when using keyboard
  const openAndFocusFirst = (key) => {
    setOpen(key);
    // Allow DOM to update then focus first submenu button
    setTimeout(() => {
      const el = rootRef.current?.querySelector(`#submenu-${key} button`);
      if (el) el.focus();
    }, 0);
  };

  const handleButtonKeyDown = (e, key) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      toggle(key);
      if (!(open === key)) openAndFocusFirst(key);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      openAndFocusFirst(key);
    } else if (e.key === 'Escape') {
      setOpen(null);
    }
  };

  return (
    <header className="topnav">
      <div ref={rootRef} className="topnav-inner container d-flex align-items-center justify-content-between">
        <div className="d-flex align-items-center gap-3 brand-wrap" onClick={() => onNavigate('dashboard')}>
          <div className="brand" aria-hidden>
            {/* University logo: use the dev server public asset in dev, otherwise request from backend */}
            <img
              src={window.location.port === '3000' ? '/ueb-logo.png' : '/img/ueb-logo.png'}
              alt="Universidad Evangélica Boliviana"
              className="brand-logo"
            />
          </div>
          <div>
            <div className="site-title">Facultad de Tecnologia</div>
            <div className="site-subtitle">Gestión de Laboratorios</div>
          </div>
        </div>

        <button className="hamburger d-md-none" aria-label="abrir menu" aria-expanded={mobileOpen} onClick={() => setMobileOpen(!mobileOpen)}>
          ☰
        </button>

        <nav className={`menu d-flex align-items-center ${mobileOpen ? 'open' : ''}`} aria-label="Principal">
          <div
            className={`menu-item ${open === 'registro' ? 'open' : ''}`}
            onMouseEnter={() => setOpen('registro')}
            onMouseLeave={() => setOpen(null)}
          >
            <button
              className={`menu-button ${open === 'registro' ? 'active' : ''}`}
              onClick={() => toggle('registro')}
              onFocus={() => setOpen('registro')}
              onKeyDown={(e) => handleButtonKeyDown(e, 'registro')}
              aria-haspopup="true"
              aria-controls="submenu-registro"
              aria-expanded={open === 'registro'}
            >
              Configuración ▾
            </button>
                {open === 'registro' && (
                  <div id="submenu-registro" className="submenu" role="menu" onMouseEnter={() => setOpen('registro')} onMouseLeave={() => setOpen(null)}>
                    <button role="menuitem" onClick={() => onNavigate('personas')}>Registro de persona</button>
                    <button role="menuitem" onClick={() => onNavigate('registro_tarjeta')}>Registro de tarjeta</button>
                    <button role="menuitem" onClick={() => onNavigate('tipo_movimiento')}>Tipo de movimiento</button>
                    <button role="menuitem" onClick={() => onNavigate('tipo_registro')}>Tipo de registro</button>
                    <button role="menuitem" onClick={() => onNavigate('perfil_persona')}>Perfil de persona</button>
                  </div>
                )}
          </div>

          <div
            className={`menu-item ${open === 'enrolar' ? 'open' : ''}`}
            onMouseEnter={() => setOpen('enrolar')}
            onMouseLeave={() => setOpen(null)}
          >
            <button
              className={`menu-button ${open === 'enrolar' ? 'active' : ''}`}
              onClick={() => toggle('enrolar')}
              onFocus={() => setOpen('enrolar')}
              onKeyDown={(e) => handleButtonKeyDown(e, 'enrolar')}
              aria-haspopup="true"
              aria-controls="submenu-enrolar"
              aria-expanded={open === 'enrolar'}
            >
              Enrolar ▾
            </button>
            {open === 'enrolar' && (
              <div id="submenu-enrolar" className="submenu" role="menu" onMouseEnter={() => setOpen('enrolar')} onMouseLeave={() => setOpen(null)}>
                <button role="menuitem" onClick={() => onNavigate('enrolar')}>Enrolar</button>
              </div>
            )}
          </div>

          <div
            className={`menu-item ${open === 'seguridad' ? 'open' : ''}`}
            onMouseEnter={() => setOpen('seguridad')}
            onMouseLeave={() => setOpen(null)}
          >
            <button
              className={`menu-button ${open === 'seguridad' ? 'active' : ''}`}
              onClick={() => toggle('seguridad')}
              onFocus={() => setOpen('seguridad')}
              onKeyDown={(e) => handleButtonKeyDown(e, 'seguridad')}
              aria-haspopup="true"
              aria-controls="submenu-seguridad"
              aria-expanded={open === 'seguridad'}
            >
              Seguridad ▾
            </button>
            {open === 'seguridad' && (
              <div id="submenu-seguridad" className="submenu" role="menu" onMouseEnter={() => setOpen('seguridad')} onMouseLeave={() => setOpen(null)}>
                <button role="menuitem" onClick={() => onNavigate('usuarios')}>Usuarios</button>
                <button role="menuitem" onClick={() => onNavigate('permisos')}>Permisos</button>
                <button role="menuitem" onClick={() => onNavigate('roles')}>Roles</button>
                <button role="menuitem" onClick={() => onNavigate('bitacora')}>Bitácora</button>
              </div>
            )}
          </div>

          <div
            className={`menu-item ${open === 'reportes' ? 'open' : ''}`}
            onMouseEnter={() => setOpen('reportes')}
            onMouseLeave={() => setOpen(null)}
          >
            <button
              className={`menu-button ${open === 'reportes' ? 'active' : ''}`}
              onClick={() => toggle('reportes')}
              onFocus={() => setOpen('reportes')}
              onKeyDown={(e) => handleButtonKeyDown(e, 'reportes')}
              aria-haspopup="true"
              aria-controls="submenu-reportes"
              aria-expanded={open === 'reportes'}
            >
              Reportes ▾
            </button>
            {open === 'reportes' && (
              <div id="submenu-reportes" className="submenu" role="menu" onMouseEnter={() => setOpen('reportes')} onMouseLeave={() => setOpen(null)}>
                <button role="menuitem" onClick={() => onNavigate('reportes_ingresos')}>Ingresos de personas</button>
                <button role="menuitem" onClick={() => onNavigate('tarjetas_historial')}>Historial tarjetas</button>
                <button role="menuitem" onClick={() => onNavigate('accesos_historial')}>Historial accesos</button>
              </div>
            )}
          </div>

          <div className="user-actions d-flex align-items-center ms-3">
            <div className="user-name me-3">{usuario}</div>
              <button className="btn btn-danger" onClick={onLogout}> Cerrar sesión</button>
            </div>
        </nav>
      </div>
    </header>
  );
}
