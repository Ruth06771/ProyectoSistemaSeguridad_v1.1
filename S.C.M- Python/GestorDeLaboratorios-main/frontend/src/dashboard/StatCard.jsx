import React from 'react';

export default function StatCard({ title, value, color = 'primary', onClick, subtitle, icon }) {
  const colorClass = `card-${color}`;
  return (
    <div className={`card text-white ${colorClass} card-hover`} style={{border:'none'}} aria-label={`${title} stat card`}>
      <div className="card-body d-flex align-items-center justify-content-between">
        <div>
          <div className="stat-title">{title}</div>
          <div className="stat-value">{value}</div>
          {subtitle && <div className="small opacity-75">{subtitle}</div>}
        </div>
        <div className="ms-3">{icon}</div>
      </div>
      {onClick && (
        <div className="card-footer bg-transparent border-0">
          <button className="btn btn-light btn-sm w-100" onClick={onClick}>Ver</button>
        </div>
      )}
    </div>
  );
}
