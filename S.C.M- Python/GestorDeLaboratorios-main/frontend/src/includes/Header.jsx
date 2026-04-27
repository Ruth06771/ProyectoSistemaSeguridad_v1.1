import React from 'react';

export default function Header({ usuario, onLogout }) {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
      <div className="container">
        <a className="navbar-brand" href="#">Panel Administracin</a>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavAltMarkup"
          aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNavAltMarkup">
          <ul className="navbar-nav ms-auto">
            <li className="nav-item">
              <span className="navbar-text text-white me-3">
                Hola, {usuario}
              </span>
            </li>
            <li className="nav-item">
              <button onClick={onLogout} className="btn btn-outline-light btn-sm">Cerrar sesin</button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}
import React from 'react';

export default function Header({ usuario, onLogout }) {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
      <div className="container">
        <a className="navbar-brand" href="#">Panel Administración</a>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavAltMarkup"
          aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNavAltMarkup">
          <ul className="navbar-nav ms-auto">
            <li className="nav-item">
              <span className="navbar-text text-white me-3">
                Hola, {usuario}
              </span>
            </li>
            <li className="nav-item">
              <button onClick={onLogout} className="btn btn-outline-light btn-sm">Cerrar sesión</button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}
