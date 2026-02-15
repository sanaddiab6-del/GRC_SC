'use client';

import { useEffect, useState } from 'react';

interface Asset {
  asset_id: string;
  name_en: string;
  asset_type: string;
  criticality: string;
  environment: string;
  status: string;
}

export default function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mock data
    setAssets([
      { asset_id: 'APP-001', name_en: 'GRC Platform', asset_type: 'application', criticality: 'critical', environment: 'production', status: 'active' },
      { asset_id: 'DB-001', name_en: 'PostgreSQL Database', asset_type: 'database', criticality: 'critical', environment: 'production', status: 'active' },
      { asset_id: 'CLOUD-001', name_en: 'Azure Cloud Environment', asset_type: 'cloud_service', criticality: 'high', environment: 'production', status: 'active' },
      { asset_id: 'NET-001', name_en: 'Firewall', asset_type: 'network_device', criticality: 'critical', environment: 'production', status: 'active' },
    ]);
    setLoading(false);
  }, []);

  const getCriticalityColor = (level: string) => {
    switch(level) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-green-100 text-green-800';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Asset Management</h1>
        
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-100 border-b">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Asset ID</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Name</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Type</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Criticality</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Environment</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-700">Status</th>
                </tr>
              </thead>
              <tbody>
                {assets.map((asset) => (
                  <tr key={asset.asset_id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-indigo-600">{asset.asset_id}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{asset.name_en}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{asset.asset_type}</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCriticalityColor(asset.criticality)}`}>
                        {asset.criticality.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{asset.environment}</td>
                    <td className="px-6 py-4">
                      <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                        {asset.status.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
