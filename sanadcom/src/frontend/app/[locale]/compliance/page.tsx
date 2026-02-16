'use client';

export default function ComplianceStatusPage() {
  const frameworks = [
    {
      framework: 'ECC',
      name: 'Essential Cybersecurity Controls',
      name_ar: 'ضوابط الأمن السيبراني الأساسية',
      compliance: 75,
      controls_total: 4,
      controls_compliant: 3,
      status: 'good'
    },
    {
      framework: 'CCC',
      name: 'Cloud Cybersecurity Controls',
      name_ar: 'ضوابط أمن الحوسبة السحابية',
      compliance: 60,
      controls_total: 5,
      controls_compliant: 3,
      status: 'needs_attention'
    },
    {
      framework: 'PDPL',
      name: 'Personal Data Protection Law',
      name_ar: 'قانون حماية البيانات الشخصية',
      compliance: 80,
      controls_total: 8,
      controls_compliant: 6,
      status: 'good'
    },
    {
      framework: 'ISO 27001',
      name: 'Information Security Management',
      name_ar: 'إدارة أمن المعلومات',
      compliance: 70,
      controls_total: 14,
      controls_compliant: 10,
      status: 'good'
    }
  ];

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'needs_attention': return 'bg-orange-100 text-orange-800';
      case 'good': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const overallCompliance = Math.round((75 + 60 + 80 + 70) / 4);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Compliance Status</h1>

        {/* Overall Score */}
        <div className="bg-white rounded-lg shadow p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Overall Compliance Score</h2>
              <p className="text-gray-600 mt-2">Across all regulatory frameworks</p>
            </div>
            <div className="text-6xl font-bold text-indigo-600">{overallCompliance}%</div>
          </div>
          
          <div className="mt-6 w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-indigo-600 h-3 rounded-full" 
              style={{ width: `${overallCompliance}%` }}
            ></div>
          </div>
        </div>

        {/* Frameworks Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {frameworks.map((fw) => (
            <div key={fw.framework} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{fw.framework}</h3>
                  <p className="text-sm text-gray-600">{fw.name}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(fw.status)}`}>
                  {fw.status === 'needs_attention' ? 'Review' : fw.status === 'critical' ? 'Critical' : 'On Track'}
                </span>
              </div>

              <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-semibold text-gray-700">Controls Compliance</span>
                  <span className="text-sm font-bold text-gray-900">{fw.compliance}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${fw.compliance >= 80 ? 'bg-green-500' : fw.compliance >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                    style={{ width: `${fw.compliance}%` }}
                  ></div>
                </div>
              </div>

              <div className="text-sm text-gray-600">
                {fw.controls_compliant} of {fw.controls_total} controls compliant
              </div>
            </div>
          ))}
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-3xl font-bold text-green-600">31</div>
            <div className="text-gray-600 text-sm">Total Controls</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-3xl font-bold text-orange-600">3</div>
            <div className="text-gray-600 text-sm">Open Findings</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-3xl font-bold text-red-600">2</div>
            <div className="text-gray-600 text-sm">Overdue Items</div>
          </div>
        </div>
      </div>
    </div>
  );
}
