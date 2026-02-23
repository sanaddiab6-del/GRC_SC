// Usage examples for PermissionGuard and usePermission
import { PermissionGuard } from '@/components/PermissionGuard';
import { usePermission } from '@/lib/role-guard';

export function ApproveEvidenceButton() {
  const canApprove = usePermission('approve_evidence');
  return (
    <PermissionGuard action="approve_evidence" fallback={null}>
      <button className="btn btn-primary">Approve Evidence</button>
    </PermissionGuard>
  );
}

export function DeleteControlButton() {
  return (
    <PermissionGuard action="delete_control" fallback={<span>Not allowed</span>} mode="disable">
      <button className="btn btn-danger">Delete Control</button>
    </PermissionGuard>
  );
}

export function ReportsPage() {
  // Hide entire page if not allowed
  return (
    <PermissionGuard action="view_reports">
      <div>Reports content here...</div>
    </PermissionGuard>
  );
}
