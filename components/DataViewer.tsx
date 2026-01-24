import React, { useState, useMemo } from 'react';
import { Ticket } from '../types';
import { Search, Filter, AlertTriangle, Layers, Activity } from './Icons';

interface DataViewerProps {
  data: Ticket[];
}

export const DataViewer: React.FC<DataViewerProps> = ({ data }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'CONFLICTS' | 'OVERDUE' | 'CRITICAL'>('ALL');

  // Calculate Metrics & Derived State
  const stats = useMemo(() => {
    const idCounts = data.reduce((acc, t) => {
      acc[t.id] = (acc[t.id] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    // Find IDs that appear more than once
    const conflictIds = Object.keys(idCounts).filter(id => idCounts[id] > 1);
    
    // Count specific issues
    const overdueCount = data.filter(t => new Date(t.dueDate) < new Date() && t.status !== 'Closed').length;
    const criticalCount = data.filter(t => t.priority === 'Critical').length;

    return {
      total: data.length,
      conflicts: conflictIds.length,
      conflictIds, // List of IDs that are conflicting
      overdue: overdueCount,
      critical: criticalCount
    };
  }, [data]);

  // Filter Data based on UI controls
  const filteredData = useMemo(() => {
    return data.filter(ticket => {
      // 1. Text Search
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = 
        ticket.title.toLowerCase().includes(searchLower) ||
        ticket.id.toLowerCase().includes(searchLower) ||
        ticket.customer.toLowerCase().includes(searchLower) ||
        ticket.source.toLowerCase().includes(searchLower);
      
      if (!matchesSearch) return false;

      // 2. Category Filter
      if (activeFilter === 'CONFLICTS') return stats.conflictIds.includes(ticket.id);
      if (activeFilter === 'OVERDUE') return new Date(ticket.dueDate) < new Date() && ticket.status !== 'Closed';
      if (activeFilter === 'CRITICAL') return ticket.priority === 'Critical';

      return true;
    });
  }, [data, searchTerm, activeFilter, stats]);

  return (
    <div className="space-y-6 pb-20">
      
      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex flex-col justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Records</span>
            <span className="text-2xl font-bold text-white mt-1">{stats.total}</span>
        </div>
        <div className={`bg-slate-900/60 border p-4 rounded-xl flex flex-col justify-between ${stats.conflicts > 0 ? 'border-amber-900/50 bg-amber-500/5' : 'border-slate-800'}`}>
            <span className={`text-xs font-bold uppercase tracking-wider ${stats.conflicts > 0 ? 'text-amber-500' : 'text-slate-500'}`}>Conflicts Found</span>
            <span className={`text-2xl font-bold mt-1 ${stats.conflicts > 0 ? 'text-amber-400' : 'text-slate-200'}`}>{stats.conflicts}</span>
        </div>
        <div className={`bg-slate-900/60 border p-4 rounded-xl flex flex-col justify-between ${stats.overdue > 0 ? 'border-rose-900/50 bg-rose-500/5' : 'border-slate-800'}`}>
            <span className={`text-xs font-bold uppercase tracking-wider ${stats.overdue > 0 ? 'text-rose-500' : 'text-slate-500'}`}>SLA Breaches</span>
            <span className={`text-2xl font-bold mt-1 ${stats.overdue > 0 ? 'text-rose-400' : 'text-slate-200'}`}>{stats.overdue}</span>
        </div>
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex flex-col justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Critical Items</span>
            <span className="text-2xl font-bold text-white mt-1">{stats.critical}</span>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="relative w-full md:w-96">
            <input 
                type="text" 
                placeholder="Search by ID, Customer, or Title..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg py-2.5 pl-10 pr-4 text-sm text-slate-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
            />
            <Search className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-2 md:pb-0">
            <button 
                onClick={() => setActiveFilter('ALL')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wide transition-all whitespace-nowrap border ${activeFilter === 'ALL' ? 'bg-slate-800 text-white border-slate-600' : 'bg-transparent text-slate-500 border-transparent hover:bg-slate-900'}`}
            >
                All Data
            </button>
            <button 
                onClick={() => setActiveFilter('CONFLICTS')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wide transition-all whitespace-nowrap border ${activeFilter === 'CONFLICTS' ? 'bg-amber-950/40 text-amber-400 border-amber-900/50' : 'bg-transparent text-slate-500 border-transparent hover:bg-slate-900'}`}
            >
                <Layers className="w-3 h-3" />
                Conflicts ({stats.conflicts})
            </button>
            <button 
                onClick={() => setActiveFilter('OVERDUE')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wide transition-all whitespace-nowrap border ${activeFilter === 'OVERDUE' ? 'bg-rose-950/40 text-rose-400 border-rose-900/50' : 'bg-transparent text-slate-500 border-transparent hover:bg-slate-900'}`}
            >
                <Activity className="w-3 h-3" />
                Breaches ({stats.overdue})
            </button>
            <button 
                onClick={() => setActiveFilter('CRITICAL')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wide transition-all whitespace-nowrap border ${activeFilter === 'CRITICAL' ? 'bg-purple-950/40 text-purple-400 border-purple-900/50' : 'bg-transparent text-slate-500 border-transparent hover:bg-slate-900'}`}
            >
                Critical ({stats.critical})
            </button>
        </div>
      </div>

      {/* Data Table */}
      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-700 bg-slate-950/50">
                <th className="p-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Source</th>
                <th className="p-4 text-xs font-bold text-slate-400 uppercase tracking-wider">ID</th>
                <th className="p-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Title</th>
                <th className="p-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Customer</th>
                <th className="p-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Status</th>
                <th className="p-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Due Date</th>
                <th className="p-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Priority</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {filteredData.length > 0 ? filteredData.map((ticket, idx) => {
                // Determine row styling
                const isConflict = stats.conflictIds.includes(ticket.id);
                const isOverdue = new Date(ticket.dueDate) < new Date() && ticket.status !== 'Closed';

                return (
                  <tr key={`${ticket.id}-${idx}`} className={`group hover:bg-slate-800/50 transition-colors ${isConflict && activeFilter !== 'CONFLICTS' ? 'bg-amber-900/5' : ''}`}>
                    <td className="p-4">
                      <span className="px-2 py-1 rounded text-[10px] font-bold uppercase bg-slate-800 border border-slate-700 text-slate-400">
                        {ticket.source}
                      </span>
                    </td>
                    <td className="p-4 font-mono text-sm text-blue-400 group-hover:underline cursor-pointer flex items-center gap-2">
                      {ticket.id}
                      {isConflict && (
                          <div className="relative group/tooltip">
                            <Layers className="w-3.5 h-3.5 text-amber-500" />
                            <div className="absolute left-full ml-2 top-1/2 -translate-y-1/2 hidden group-hover/tooltip:block z-50 w-48 p-2 bg-slate-900 text-xs text-slate-200 rounded border border-slate-700 shadow-xl">
                                Conflict Detected: Multiple sources reporting different states.
                            </div>
                          </div>
                      )}
                    </td>
                    <td className="p-4 text-sm font-medium text-slate-200">
                      {ticket.title}
                    </td>
                    <td className="p-4 text-sm text-slate-400">
                      {ticket.customer}
                    </td>
                    <td className="p-4">
                       <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide border ${
                          ticket.status === 'Closed' || ticket.status === 'Resolved' ? 'bg-emerald-950/50 text-emerald-400 border-emerald-900/50' : 
                          ticket.status === 'Open' ? 'bg-blue-950/50 text-blue-400 border-blue-900/50' : 
                          'bg-slate-800 text-slate-400 border-slate-700'
                       }`}>
                         {ticket.status}
                       </span>
                    </td>
                    <td className="p-4">
                        <div className="flex items-center gap-2">
                            <span className={`text-sm font-mono ${isOverdue ? 'text-rose-400 font-bold' : 'text-slate-400'}`}>
                                {ticket.dueDate}
                            </span>
                            {isOverdue && <AlertTriangle className="w-3 h-3 text-rose-500" />}
                        </div>
                    </td>
                    <td className="p-4">
                      <span className={`text-xs font-bold ${
                          ticket.priority === 'Critical' ? 'text-rose-500' : 
                          ticket.priority === 'High' ? 'text-amber-500' : 'text-slate-500'
                      }`}>
                          {ticket.priority}
                      </span>
                    </td>
                  </tr>
                );
              }) : (
                  <tr>
                      <td colSpan={7} className="p-12 text-center text-slate-500">
                          <Filter className="w-8 h-8 mx-auto mb-3 opacity-20" />
                          <p>No records found matching current filters.</p>
                      </td>
                  </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};