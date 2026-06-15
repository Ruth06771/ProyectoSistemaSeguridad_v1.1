import React, { useEffect, useState } from 'react';

const readPermissions = () => {
  try {
    const raw = window.localStorage.getItem('permissions');
    return raw ? JSON.parse(raw) : {};
  } catch (error) {
    return {};
  }
};

export const hasPermission = (permissionKey) => {
  if (!permissionKey) return false;
  const permissions = readPermissions();
  return Boolean(permissions[permissionKey]);
};

export default function PermissionGate({ permissionKey, fallback = null, children }) {
  const [allowed, setAllowed] = useState(false);

  useEffect(() => {
    setAllowed(hasPermission(permissionKey));
  }, [permissionKey]);

  if (!allowed) {
    return fallback;
  }

  return <>{children}</>;
}
