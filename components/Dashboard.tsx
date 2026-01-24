import React from 'react';
import { BriefingResponse, BriefingItem } from '../types';
import { AlertTriangle, Layers, Activity, CheckCircle, FileText, Eye } from './Icons';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface DashboardProps {
  data: BriefingResponse | null;
  loading: boolean;
  onItemClick: (item: BriefingItem) => void;
}

interface BriefingCardProps {
  item: BriefingItem;
  onClick: () => void;
}

const BriefingCard: React.FC<BriefingCardProps> = ({ item, onClick }) => {
  const isCritical = item.severity === 'CRITICAL' || item.severity === 'HIGH';
  
  // Dynamic styles based on severity
  const accentColor = isCritical ? 'text-rose-400' : 'text-amber-400';
  const accentBorder = isCritical ? 'border-rose-500/30' : 'border-amber-500/30';
  const accentBg = isCritical ? 'bg-rose-500/10' : 'bg-amber-500/10';

  return (
    <div 
      onClick={onClick}
      className={`group relative flex flex-col p-5 rounded-2xl border ${accentBorder} bg-slate-900/40 backdrop-blur-sm hover:bg-slate-800/60 hover:border-slate-600 transition-all duration-300 cursor-pointer overflow-hidden h-full`}
    >
      {/* Top Decoration Line */}
      <div className={`absolute top-0 left-0 w-full h-1 ${isCritical ? 'bg-gradient-to-r from-rose-500 to-transparent' : 'bg-gradient-to-r from-amber-500 to-transparent'} opacity-50`} />

      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${accentBg}`}>
            {item.type === 'DATA_CONFLICT' ? (
              <Layers className={`w-5 h-5 ${accentColor}`} />
            ) : (
              <AlertTriangle className={`w-5 h-5 ${accentColor}`} />
            )}
          </div>
          <div>
             <div className={`text-[10px] font-bold uppercase tracking-widest ${accentColor} mb-0.5`}>
               {item.type.replace('_', ' ')}
             </div>
             <div className="text-xs text-slate-500 font-mono">
               ID: {item.relatedTicketIds[0]}
             </div>
          </div>
        </div>
        <div className={`px-2 py-0.5 rounded text-[10px] font-bold border ${accentBorder} ${accentColor} bg-slate-950/30 uppercase`}>
            {item.severity}
        </div>
      </div>

      {/* Content */}
      <h3 className="text-base font-semibold text-slate-100 mb-2 leading-tight group-hover:text-blue-300 transition-colors">
        {item.title}
      </h3>
      <p className="text-slate-400 text-sm leading-relaxed mb-6 flex-grow">
        {item.description}
      </p>

      {/* Action Footer - Now fully visible */}
      {item.suggestedAction && (
        <div className="mt-auto pt-4 border-t border-slate-800/50">
          <div className="flex flex-col gap-2 group-hover:translate-x-1 transition-transform duration-300">
             <span className="text-[10px] text-emerald-500 font-bold uppercase tracking-wider">Recommended Action</span>
             <div className="bg-emerald-950/30 border border-emerald-900/50 rounded-lg p-3">
                <span className="text-xs text-slate-300 whitespace-normal leading-relaxed block">
                  {item.suggestedAction}
                </span>
             </div>
          </div>
        </div>
      )}
    </div>
  );
};

const chartData = [
  { name: 'On Track', value: 35, color: '#10b981' }, 
  { name: 'At Risk', value: 10, color: '#f59e0b' }, 
  { name: 'Critical', value: 5, color: '#f43f5e' }, 
];

export const Dashboard: React.FC<DashboardProps> = ({ data, loading, onItemClick }) => {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-4 animate-pulse">
        <div className="relative">
          <div className="absolute inset-0 bg-blue-500 blur-xl opacity-20 rounded-full"></div>
          <Activity className="w-16 h-16 text-blue-500 animate-spin relative z-10" />
        </div>
        <p className="text-slate-400 text-lg font-light tracking-wide">INITIALIZING NIGHT WATCHMAN PROTOCOL...</p>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6 animate-fade-in pb-20">
      
      {/* Top Section: Summary & Stats Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Briefing Text */}
        <div className="lg:col-span-2 bg-slate-900/60 backdrop-blur-md border border-slate-700/50 p-8 rounded-3xl relative overflow-hidden shadow-2xl">
           <div className="absolute top-0 right-0 p-32 bg-blue-600/10 rounded-full blur-3xl pointer-events-none -mr-16 -mt-16"></div>
           <h2 className="text-xs font-bold text-blue-400 uppercase tracking-widest mb-3 flex items-center gap-2">
              <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"/> 
              Daily Intelligence Briefing
           </h2>
           <h1 className="text-2xl md:text-3xl font-bold text-white mb-4 leading-tight">
             {data.summary}
           </h1>
           <div className="flex items-center gap-4 text-sm text-slate-400">
             <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-950 border border-slate-800">
                <Activity className="w-4 h-4"/> 
                Active Scans: 24/7
             </span>
             <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-950 border border-slate-800">
                <Layers className="w-4 h-4"/> 
                Sources: 8
             </span>
           </div>
        </div>

        {/* Chart Card */}
        <div className="bg-slate-900/60 backdrop-blur-md border border-slate-700/50 p-6 rounded-3xl flex flex-col justify-center relative overflow-hidden shadow-2xl">
           <div className="absolute bottom-0 left-0 p-24 bg-emerald-600/5 rounded-full blur-3xl pointer-events-none -ml-12 -mb-12"></div>
           <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 z-10">SLA Health Status</h3>
           <div className="flex-1 min-h-[140px] relative z-10">
             <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={60}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                    itemStyle={{ color: '#e2e8f0' }}
                  />
                </PieChart>
             </ResponsiveContainer>
             {/* Center Text */}
             <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-2xl font-bold text-white">85%</span>
                <span className="text-[10px] text-slate-500 uppercase">Health</span>
             </div>
           </div>
        </div>
      </div>

      <div className="h-px bg-slate-800/50 w-full my-2"></div>

      {/* Grid of Briefing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {data.items.map((item) => (
          <BriefingCard key={item.id} item={item} onClick={() => onItemClick(item)} />
        ))}
        
        {/* Empty State */}
        {data.items.length === 0 && (
           <div className="col-span-full py-16 text-center border border-dashed border-slate-800 rounded-2xl bg-slate-900/20">
             <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-500/10 rounded-full mb-4 ring-1 ring-emerald-500/20">
               <Activity className="w-8 h-8 text-emerald-500" />
             </div>
             <h3 className="text-xl font-medium text-slate-200">All Systems Nominal</h3>
             <p className="text-slate-500 mt-2 max-w-md mx-auto">No critical anomalies or SLA breaches detected in the last scan. The operational grid is clean.</p>
           </div>
        )}
      </div>

      <div className="h-px bg-slate-800/50 w-full my-6"></div>

      {/* Connected Workspace Apps Section */}
      <div>
        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4">Connected Workspace Apps</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* App 1: IMACD Playbook */}
            <div className="p-4 bg-slate-900/40 border border-slate-800 hover:border-blue-500/30 rounded-xl transition-all hover:-translate-y-1 cursor-pointer group">
                <div className="w-10 h-10 rounded-lg bg-blue-900/20 flex items-center justify-center mb-3 group-hover:bg-blue-600/20 transition-colors">
                    <Layers className="w-5 h-5 text-blue-400" />
                </div>
                <div className="font-semibold text-slate-200 text-sm">IMACD Playbook</div>
                <div className="text-xs text-slate-500 mt-1">Asset lifecycle orchestration</div>
            </div>
             {/* App 2: Contract Updater */}
            <div className="p-4 bg-slate-900/40 border border-slate-800 hover:border-emerald-500/30 rounded-xl transition-all hover:-translate-y-1 cursor-pointer group">
                <div className="w-10 h-10 rounded-lg bg-emerald-900/20 flex items-center justify-center mb-3 group-hover:bg-emerald-600/20 transition-colors">
                    <FileText className="w-5 h-5 text-emerald-400" />
                </div>
                <div className="font-semibold text-slate-200 text-sm">Provider Contracts</div>
                <div className="text-xs text-slate-500 mt-1">System-of-record write-back</div>
            </div>
            {/* App 3: VMO Insights */}
             <div className="p-4 bg-slate-900/40 border border-slate-800 hover:border-purple-500/30 rounded-xl transition-all hover:-translate-y-1 cursor-pointer group">
                <div className="w-10 h-10 rounded-lg bg-purple-900/20 flex items-center justify-center mb-3 group-hover:bg-purple-600/20 transition-colors">
                    <Eye className="w-5 h-5 text-purple-400" />
                </div>
                <div className="font-semibold text-slate-200 text-sm">VMO Explorer</div>
                <div className="text-xs text-slate-500 mt-1">Vendor performance feeds</div>
            </div>
            {/* App 4: SLA Micro-Report */}
             <div className="p-4 bg-slate-900/40 border border-slate-800 hover:border-rose-500/30 rounded-xl transition-all hover:-translate-y-1 cursor-pointer group">
                <div className="w-10 h-10 rounded-lg bg-rose-900/20 flex items-center justify-center mb-3 group-hover:bg-rose-600/20 transition-colors">
                    <Activity className="w-5 h-5 text-rose-400" />
                </div>
                <div className="font-semibold text-slate-200 text-sm">SLA Micro-Report</div>
                <div className="text-xs text-slate-500 mt-1">KPI & anomaly detection</div>
            </div>
        </div>
      </div>
    </div>
  );
};