'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function EnterpriseGRCDashboard() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  // Real enterprise metrics
  const metrics = [
    { 
      label: 'NCA Compliance Score', 
      value: '92%', 
      icon: 'OK',
      trend: '+5%',
      trendUp: true,
      details: 'ECC: 95% | CCC: 88% | PDPL: 94%'
    },
    { 
      label: 'High Risk Items', 
      value: '7', 
      icon: 'RSK',
      trend: '-3',
      trendUp: true,
      details: 'Cyber: 4 | Compliance: 2 | Operational: 1'
    },
    { 
      label: 'Open Audit Findings', 
      value: '12', 
      icon: 'AUD',
      trend: '-8',
      trendUp: true,
      details: 'Critical: 2 | High: 5 | Medium: 5'
    },
    { 
      label: 'Critical Assets', 
      value: '89', 
      icon: 'AST',
      trend: '+12',
      trendUp: false,
      details: 'Protected by 142 controls'
    }
  ];

  // Compliance framework status
  const frameworks = [
    { name: 'NCA ECC', score: 95, controls: '142/150', color: 'bg-green-500' },
    { name: 'NCA CCC', score: 88, controls: '88/100', color: 'bg-blue-500' },
    { name: 'PDPL', score: 94, controls: '47/50', color: 'bg-purple-500' },
    { name: 'ISO 27001', score: 82, controls: '94/114', color: 'bg-yellow-500' },
  ];

  // Recent security incidents
  const incidents = [
    { 
      id: 'INC-001', 
      title: 'Ransomware Attack Attempt', 
      severity: 'critical', 
      status: 'Blocked by EDR',
      time: '2 hours ago'
    },
    { 
      id: 'INC-002', 
      title: 'Failed Login Attempts (1,245)', 
      severity: 'high', 
      status: 'Investigating',
      time: '5 hours ago'
    },
    { 
      id: 'INC-003', 
      title: 'Malware Detected & Quarantined', 
      severity: 'medium', 
      status: 'Resolved',
      time: '1 day ago'
    },
  ];

  // Risk heat map data (simplified for display)
  const riskCategories = [
    { name: 'Critical', count: 7, color: 'bg-red-600' },
    { name: 'High', count: 12, color: 'bg-orange-500' },
    { name: 'Medium', count: 24, color: 'bg-yellow-500' },
    { name: 'Low', count: 38, color: 'bg-green-500' },
  ];

  // Module navigation cards
  const modules = [
    {
      title: 'Compliance Management',
      description: 'NCA ECC/CCC/PDPL Framework Tracking',
      icon: 'CMP',
      href: '/en/compliance',
      color: 'from-blue-500 to-indigo-600',
      stats: '92% Compliant'
    },
    {
      title: 'Risk Register',
      description: 'Enterprise Risk Assessment & Treatment',
      icon: 'RSK',
      href: '/en/risks',
      color: 'from-red-500 to-orange-600',
      stats: '81 Risks Tracked'
    },
    {
      title: 'Asset Inventory',
      description: 'IT Assets, Cloud Services, Data',
      icon: 'AST',
      href: '/en/assets',
      color: 'from-purple-500 to-pink-600',
      stats: '243 Assets'
    },
    {
      title: 'Audit Programs',
      description: 'Internal & External Audits',
      icon: 'AUD',
      href: '/en/audits',
      color: 'from-green-500 to-teal-600',
      stats: '2 Active Programs'
    },
    {
      title: 'PDPL Compliance',
      description: 'Data Protection & Privacy',
      icon: 'PDPL',
      href: '/en/pdpl',
      color: 'from-indigo-500 to-purple-600',
      stats: '48 RoPA Records'
    },
    {
      title: 'Vendor Risk',
      description: 'Third-Party Risk Assessment',
      icon: 'VND',
      href: '/en/vendors',
      color: 'from-yellow-500 to-orange-600',
      stats: '42 Vendors'
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Top Navigation Bar */}
      <nav className="bg-slate-800/90 backdrop-blur-sm border-b border-slate-700/50 sticky top-0 z-50">
        <div className="max-w-[1600px] mx-auto px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-indigo-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">SG</span>
                </div>
                <div>
                  <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-600 bg-clip-text text-transparent">
                    SICO GRC
                  </div>
                  <div className="text-xs text-gray-400">Enterprise Platform</div>
                </div>
              </div>
              <div className="hidden md:flex items-center space-x-4 ml-8">
                <Link href="/en/enterprise-dashboard" className="text-blue-400 font-semibold">Dashboard</Link>
                <Link href="/en/compliance" className="text-gray-300 hover:text-white transition">Compliance</Link>
                <Link href="/en/risks" className="text-gray-300 hover:text-white transition">Risks</Link>
                <Link href="/en/assets" className="text-gray-300 hover:text-white transition">Assets</Link>
                <Link href="/en/audits" className="text-gray-300 hover:text-white transition">Audits</Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm">
                <span className="text-gray-400">SA</span>
                <span className="text-green-400 font-semibold">NCA Compliant</span>
              </div>
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center text-white font-bold">
                A
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-[1600px] mx-auto px-8 py-8">
        
        {/* Header Section */}
        <div className="mb-12">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">
                Executive Dashboard
              </h1>
              <p className="text-gray-400 text-lg">
                Saudi National Bank - Real-time Compliance & Risk Monitoring
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400">Last Updated</div>
              <div className="text-white font-semibold">11 Feb 2026, 10:45 AM</div>
            </div>
          </div>
        </div>

        {/* Key Performance Indicators */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {metrics.map((metric, idx) => (
            <div 
              key={idx}
              className="bg-gradient-to-br from-slate-800 to-slate-800/50 rounded-xl p-6 border border-slate-700/50 hover:border-blue-500/50 transition-all hover:-translate-y-1 hover:shadow-2xl hover:shadow-blue-500/20 cursor-pointer"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="text-xs font-semibold tracking-wide text-slate-300">{metric.icon}</div>
                <div className={`text-sm font-semibold px-2 py-1 rounded ${metric.trendUp ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                  {metric.trend}
                </div>
              </div>
              <div className="text-gray-400 text-sm mb-2">{metric.label}</div>
              <div className="text-4xl font-bold text-white mb-2">{metric.value}</div>
              <div className="text-xs text-gray-500 mt-2">{metric.details}</div>
            </div>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          
          {/* Left Column - Compliance Status */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* Compliance Framework Status */}
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
              <h2 className="text-2xl font-bold text-white mb-6">NCA Compliance Status</h2>
              <div className="space-y-4">
                {frameworks.map((framework, idx) => (
                  <div key={idx}>
                    <div className="flex justify-between mb-2">
                      <span className="text-gray-300 font-semibold">{framework.name}</span>
                      <span className="text-white font-bold">{framework.score}%</span>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
                      <div 
                        className={`h-full ${framework.color} rounded-full transition-all duration-500`}
                        style={{ width: `${framework.score}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">{framework.controls} controls implemented</div>
                  </div>
                ))}
              </div>
              <div className="mt-6 pt-6 border-t border-slate-700">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Overall Compliance</span>
                  <span className="text-3xl font-bold text-green-400">92%</span>
                </div>
              </div>
            </div>

            {/* Risk Heat Map */}
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
              <h2 className="text-2xl font-bold text-white mb-6">Risk Distribution</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {riskCategories.map((category, idx) => (
                  <div key={idx} className="text-center">
                    <div className={`${category.color} w-full h-32 rounded-lg flex items-center justify-center mb-2 hover:scale-105 transition cursor-pointer`}>
                      <span className="text-5xl font-bold text-white">{category.count}</span>
                    </div>
                    <div className="text-gray-300 font-semibold">{category.name}</div>
                  </div>
                ))}
              </div>
              <div className="mt-6 text-center">
                <span className="text-gray-400 text-sm">Total Identified Risks: </span>
                <span className="text-white font-bold text-lg">81</span>
              </div>
            </div>

          </div>

          {/* Right Column - Recent Activity */}
          <div className="space-y-8">
            
            {/* Security Incidents */}
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
              <h2 className="text-xl font-bold text-white mb-4">Security Incidents</h2>
              <div className="space-y-3">
                {incidents.map((incident, idx) => (
                  <div 
                    key={idx}
                    className={`p-4 rounded-lg border-l-4 ${
                      incident.severity === 'critical' ? 'bg-red-500/10 border-red-500' :
                      incident.severity === 'high' ? 'bg-orange-500/10 border-orange-500' :
                      'bg-green-500/10 border-green-500'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-xs text-gray-400 font-mono">{incident.id}</span>
                      <span className={`text-xs px-2 py-1 rounded font-semibold ${
                        incident.severity === 'critical' ? 'bg-red-500 text-white' :
                        incident.severity === 'high' ? 'bg-orange-500 text-white' :
                        'bg-green-500 text-white'
                      }`}>
                        {incident.severity.toUpperCase()}
                      </span>
                    </div>
                    <div className="text-white font-semibold text-sm mb-1">{incident.title}</div>
                    <div className="text-xs text-gray-400">{incident.status}</div>
                    <div className="text-xs text-gray-500 mt-2">{incident.time}</div>
                  </div>
                ))}
              </div>
              <button className="w-full mt-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm font-semibold transition">
                View All Incidents →
              </button>
            </div>

            {/* Quick Actions */}
            <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl p-6 text-white">
              <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <button className="w-full py-3 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-semibold transition text-left px-4">
                  Create New Risk Assessment
                </button>
                <button className="w-full py-3 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-semibold transition text-left px-4">
                  Start Audit Program
                </button>
                <button className="w-full py-3 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-semibold transition text-left px-4">
                  Generate Compliance Report
                </button>
              </div>
            </div>

          </div>
        </div>

        {/* Module Navigation Cards */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-6">GRC Modules</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {modules.map((module, idx) => (
              <Link 
                key={idx}
                href={module.href}
                className="group relative bg-gradient-to-br from-slate-800 to-slate-800/50 rounded-xl p-6 border border-slate-700/50 hover:border-blue-500/50 transition-all hover:-translate-y-2 hover:shadow-2xl hover:shadow-blue-500/20 overflow-hidden"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${module.color} opacity-0 group-hover:opacity-10 transition-opacity`}></div>
                <div className="relative z-10">
                  <div className="text-xs font-semibold tracking-wide text-slate-300 mb-4">{module.icon}</div>
                  <h3 className="text-xl font-bold text-white mb-2">{module.title}</h3>
                  <p className="text-gray-400 text-sm mb-4">{module.description}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-blue-400 font-semibold text-sm">{module.stats}</span>
                    <span className="text-blue-400 group-hover:translate-x-2 transition-transform">→</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
