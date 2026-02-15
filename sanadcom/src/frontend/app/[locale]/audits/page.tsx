'use client';

export default function AuditManagementPage() {
  const audits = [
    {
      audit_id: 'AUDIT-2024-01',
      title: 'Annual ECC Compliance Audit',
      framework: 'ECC',
      status: 'planned',
      start_date: '2024-02-15',
      end_date: '2024-03-15',
      findings: 0
    },
    {
      audit_id: 'AUDIT-2024-02',
      title: 'Cloud Security Assessment (CCC)',
      framework: 'CCC',
      status: 'in_progress',
      start_date: '2024-02-01',
      end_date: '2024-02-28',
      findings: 3
    }
  ];

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'planned': return 'bg-blue-100 text-blue-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Audit Management</h1>
        <p className="text-gray-600 mb-8">Control testing, audits, and findings management</p>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-100 border-b">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Audit ID</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Title</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Framework</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Status</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Start Date</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">End Date</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Findings</th>
                </tr>
              </thead>
              <tbody>
                {audits.map((audit) => (
                  <tr key={audit.audit_id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-indigo-600">{audit.audit_id}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{audit.title}</td>
                    <td className="px-6 py-4 text-sm font-bold text-gray-700">{audit.framework}</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(audit.status)}`}>
                        {audit.status === 'in_progress' ? 'In Progress' : audit.status.charAt(0).toUpperCase() + audit.status.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{audit.start_date}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{audit.end_date}</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded font-medium ${audit.findings > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                        {audit.findings}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="mt-8 bg-indigo-50 border-l-4 border-indigo-500 p-6 rounded">
          <h3 className="font-bold text-gray-900 mb-2">Audit Program Schedule</h3>
          <ul className="text-sm text-gray-700 space-y-2">
            <li>Internal audits: Quarterly</li>
            <li>Regulatory audits: As required by NCA/PDPL</li>
            <li>Control testing: Per control test frequency</li>
            <li>Evidence review: Continuous</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
