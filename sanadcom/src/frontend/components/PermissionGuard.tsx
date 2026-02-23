import { ReactNode } from 'react';
import { usePermission } from '../lib/role-guard';

interface PermissionGuardProps {
  action: string;
  children: ReactNode;
  fallback?: ReactNode;
  mode?: 'hide' | 'disable'; // hide: remove from DOM, disable: render but disabled
}

export function PermissionGuard({ action, children, fallback = null, mode = 'hide' }: PermissionGuardProps) {
  const allowed = usePermission(action);
  if (allowed) return <>{children}</>;
  if (mode === 'disable') {
    // Try to clone and disable the child if possible
    if (Array.isArray(children)) {
      return children.map((child, i) =>
        typeof child === 'object' && child && 'props' in child
          ? { ...child, props: { ...child.props, disabled: true } }
          : child
      );
    }
    if (typeof children === 'object' && children && 'props' in children) {
      return { ...children, props: { ...children.props, disabled: true } };
    }
    return fallback;
  }
  // mode === 'hide'
  return fallback;
}
