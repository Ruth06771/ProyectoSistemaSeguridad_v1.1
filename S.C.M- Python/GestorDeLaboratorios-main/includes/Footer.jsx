import React from 'react';

export default function Footer({ children }) {
  return (
    <footer className="bg-light text-center py-3 mt-4">
      <div className="container">
        {children ? children : '© ' + new Date().getFullYear() + ' Sistema de Gestión - Facultad de Tecnología'}
      </div>
    </footer>
  );
}
