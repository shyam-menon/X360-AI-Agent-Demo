import React, { useState, useEffect, useRef } from 'react';
import { ChatMessage, BriefingItem, Citation } from '../types';
import { Send, CheckCircle, Activity, Layers, MessageSquare, AlertTriangle, ArrowRight, Trash, FileText } from './Icons';

interface ChatInterfaceProps {
  history: ChatMessage[];
  onSendMessage: (msg: string) => void;
  isTyping: boolean;
  prefill?: string;
  mode: 'ASK' | 'DO';
  suggestedActions?: BriefingItem[];
  onRunAction?: (command: string) => void;
  onClearChat?: () => void;
}

const PROMPT_LIBRARY = [
  {
    title: "Overdue Tickets",
    prompt: "What tickets are overdue?",
    icon: AlertTriangle
  },
  {
    title: "MPS Resources",
    prompt: "Where can I find MPS resources?",
    icon: Layers
  },
  {
    title: "MDS Resources",
    prompt: "Where can I find MDS resources?",
    icon: Activity
  },
  {
    title: "Critical Priority",
    prompt: "Which tickets are Critical priority?",
    icon: MessageSquare
  }
];

// Simple Markdown Formatter Component
const FormattedMessage = ({ content }: { content: string }) => {
  const lines = content.split('\n');

  return (
    <div className="space-y-1">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        
        const isBullet = trimmed.startsWith('* ') || trimmed.startsWith('- ');
        const isNumber = /^\d+\.\s/.test(trimmed);
        
        let cleanText = line;
        if (isBullet) cleanText = trimmed.substring(2);
        if (isNumber) cleanText = trimmed.replace(/^\d+\.\s/, '');

        const parts = cleanText.split(/(\*\*.*?\*\*)/g).map((part, partIdx) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={partIdx} className="font-bold text-white">{part.slice(2, -2)}</strong>;
          }
          return <span key={partIdx}>{part}</span>;
        });

        if (isBullet) {
          return (
            <div key={idx} className="flex items-start gap-2 ml-2">
              <span className="text-blue-400 text-[10px] mt-1.5">•</span>
              <span className="flex-1 text-slate-200">{parts}</span>
            </div>
          );
        }

        if (isNumber) {
          const numberMatch = trimmed.match(/^(\d+)\./);
          const num = numberMatch ? numberMatch[1] : '1';
          return (
            <div key={idx} className="flex items-start gap-2 ml-1">
              <span className="text-blue-400 font-mono text-xs mt-0.5">{num}.</span>
              <span className="flex-1 text-slate-200">{parts}</span>
            </div>
          );
        }

        if (!trimmed) return <div key={idx} className="h-2" />;

        return <p key={idx} className="text-slate-300 leading-relaxed">{parts}</p>;
      })}
    </div>
  );
};

// Citations Display Component
const CitationsDisplay = ({ citations }: { citations: Citation[] }) => {
  const [expanded, setExpanded] = useState(false);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-4 border-t border-slate-700 pt-3">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-xs text-slate-400 hover:text-blue-400 transition-colors w-full text-left"
      >
        <FileText className="w-3.5 h-3.5" />
        <span className="font-semibold">
          {citations.length} Knowledge Base {citations.length === 1 ? 'Source' : 'Sources'}
        </span>
        <span className="ml-auto">{expanded ? '▼' : '▶'}</span>
      </button>

      {expanded && (
        <div className="mt-3 space-y-2">
          {citations.map((citation, idx) => (
            <div
              key={idx}
              className="p-3 bg-slate-900/50 border border-slate-700 rounded-lg text-xs"
            >
              <div className="flex items-start justify-between gap-2 mb-1">
                <span className="font-mono text-blue-400 font-semibold">Source {idx + 1}</span>
                <span className="text-slate-500">Score: {citation.score.toFixed(3)}</span>
              </div>

              {citation.sourceUri && (
                <div className="mt-2">
                  <a
                    href={citation.sourceUri}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 underline break-all"
                  >
                    {citation.sourceUri}
                  </a>
                </div>
              )}

              {citation.documentId && !citation.sourceUri && (
                <div className="mt-1 text-slate-400 font-mono text-[10px]">
                  Doc: {citation.documentId}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ history, onSendMessage, isTyping, prefill, mode, suggestedActions = [], onRunAction, onClearChat }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const isDoMode = mode === 'DO';
  const headerTitle = isDoMode ? 'X360 Execution Engine' : 'X360 Analyst Agent';
  const headerSubtitle = isDoMode ? 'Mode: ACTIVE EXECUTION' : 'Mode: DATA ANALYSIS';
  const placeholder = isDoMode ? 'Enter a command or playbook name...' : 'Ask a question or select a prompt...';

  useEffect(() => {
    if (prefill) {
      setInput(prefill);
    }
  }, [prefill]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [history, isTyping]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSendMessage(input);
    setInput('');
  };

  // Handler for clicking a suggested playbook in the empty state
  const handleExecutePlaybook = (item: BriefingItem) => {
     const command = `Execute remediation playbook for ${item.type} on Ticket ${item.relatedTicketIds.join(', ')}.`;
     onSendMessage(command);
  };

  // Handler for transferring from Agent to Actions
  const handleTransfer = () => {
    if (onRunAction) {
      onRunAction("Execute the playbook steps identified in the analysis.");
    }
  };

  // Handler for Prompt Library clicks
  const handlePromptClick = (prompt: string) => {
    setInput(prompt);
  };

  return (
    <div className={`flex flex-col h-full bg-slate-900/80 backdrop-blur border rounded-2xl overflow-hidden shadow-2xl transition-colors duration-500 ${isDoMode ? 'border-emerald-900/50' : 'border-slate-800'}`}>
      
      {/* Header */}
      <div className={`p-4 border-b flex items-center justify-between ${isDoMode ? 'bg-emerald-950/30 border-emerald-900/30' : 'bg-slate-950/80 border-slate-800'}`}>
        <div className="flex items-center gap-3">
           <div className={`w-2 h-2 rounded-full animate-pulse ${isDoMode ? 'bg-emerald-500' : 'bg-blue-500'}`} />
           <span className={`font-bold ${isDoMode ? 'text-emerald-100' : 'text-slate-200'}`}>{headerTitle}</span>
        </div>
        <div className="flex items-center gap-4">
            <div className={`text-xs font-mono uppercase tracking-wider ${isDoMode ? 'text-emerald-500/70' : 'text-slate-500'}`}>
            {headerSubtitle}
            </div>
            {history.length > 0 && onClearChat && (
                <button 
                    onClick={onClearChat}
                    className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                    title="Clear Chat History"
                >
                    <Trash className="w-4 h-4" />
                </button>
            )}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth relative">
        
        {/* Empty State / Prompt Library for Agent Mode */}
        {history.length === 0 && !isDoMode && (
          <div className="h-full flex flex-col items-center justify-center p-4 md:p-12 animate-fade-in">
             <div className="text-center mb-10 opacity-90 max-w-2xl">
                <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center mx-auto mb-6 border border-blue-500/20 shadow-lg shadow-blue-500/5">
                    <MessageSquare className="w-6 h-6 text-blue-400" />
                </div>
                <h2 className="text-2xl font-bold text-white mb-3">Operational Intelligence</h2>
                <p className="text-slate-400 text-sm leading-relaxed">
                   Access real-time data from Jira, Salesforce, and Datadog. Select a query below to analyze the RAG operational dataset.
                </p>
             </div>

             <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl">
                {PROMPT_LIBRARY.map((item, idx) => (
                   <button
                     key={idx}
                     onClick={() => handlePromptClick(item.prompt)}
                     className="text-left p-6 rounded-2xl bg-slate-800/40 border border-slate-700/50 hover:bg-slate-800 hover:border-blue-500/50 transition-all group duration-200 flex flex-col h-full shadow-sm hover:shadow-md hover:shadow-blue-900/10 hover:-translate-y-1"
                   >
                      <div className="flex items-center gap-3 mb-3">
                         <div className="p-2 rounded-lg bg-slate-900 group-hover:bg-blue-950/50 transition-colors">
                            <item.icon className="w-5 h-5 text-blue-400 group-hover:text-blue-300 transition-colors" />
                         </div>
                         <span className="font-bold text-slate-200 text-sm tracking-wide group-hover:text-white transition-colors">{item.title}</span>
                      </div>
                      <p className="text-sm text-slate-500 leading-relaxed group-hover:text-slate-400 transition-colors pl-1">
                        "{item.prompt}"
                      </p>
                   </button>
                ))}
             </div>
          </div>
        )}

        {/* Action Selection Screen (Only in DO mode when history is empty) */}
        {history.length === 0 && isDoMode && (
           <div className="max-w-4xl mx-auto pt-8 px-4">
              <div className="text-center mb-10">
                 <h2 className="text-2xl font-bold text-white mb-2">Remediation Playbooks Available</h2>
                 <p className="text-slate-400 text-sm">Select an identified issue to execute its standard operating procedure (SOP).</p>
              </div>
              
              <div className="grid gap-4">
                 {suggestedActions.length > 0 ? (
                    suggestedActions.map((item) => (
                       <button 
                          key={item.id}
                          onClick={() => handleExecutePlaybook(item)}
                          className="flex items-start gap-4 p-6 bg-slate-900/50 hover:bg-emerald-900/20 border border-slate-800 hover:border-emerald-500/50 rounded-2xl transition-all group text-left w-full hover:-translate-y-0.5 shadow-sm"
                       >
                          <div className={`mt-1 p-3 rounded-xl ${item.severity === 'CRITICAL' ? 'bg-rose-500/10 text-rose-500' : 'bg-amber-500/10 text-amber-500'}`}>
                             <Layers className="w-6 h-6" />
                          </div>
                          <div className="flex-1">
                             <div className="flex justify-between items-center mb-2">
                                <h3 className="font-semibold text-lg text-slate-200 group-hover:text-emerald-400 transition-colors">
                                   Run Playbook: {item.title}
                                </h3>
                                <span className={`text-[10px] font-bold uppercase px-2.5 py-1 rounded-md tracking-wider ${item.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-400 border border-rose-900/50' : 'bg-amber-950 text-amber-400 border border-amber-900/50'}`}>
                                   {item.severity}
                                </span>
                             </div>
                             <p className="text-sm text-slate-400 mb-3">Target: <span className="font-mono text-slate-300">{item.relatedTicketIds.join(', ')}</span></p>
                             <div className="flex items-center gap-2 text-xs text-emerald-600 font-mono bg-emerald-950/20 w-fit px-2 py-1 rounded">
                                <Activity className="w-3 h-3" />
                                <span>Ready to Initialize</span>
                             </div>
                          </div>
                          <div className="mt-2 self-center">
                             <div className="w-10 h-10 rounded-full bg-slate-800 group-hover:bg-emerald-600 flex items-center justify-center transition-colors shadow-inner">
                                <Send className="w-5 h-5 text-slate-400 group-hover:text-white" />
                             </div>
                          </div>
                       </button>
                    ))
                 ) : (
                    <div className="text-center p-12 border border-dashed border-slate-800 rounded-2xl bg-slate-900/30">
                       <p className="text-slate-500">No recommended playbooks found for current data.</p>
                    </div>
                 )}
              </div>
           </div>
        )}
        
        {/* Chat History */}
        {history.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div 
              className={`max-w-[85%] p-5 rounded-2xl text-sm shadow-sm ${
                msg.role === 'user' 
                  ? `${isDoMode ? 'bg-emerald-700' : 'bg-blue-600'} text-white rounded-tr-none` 
                  : 'bg-slate-800/90 border border-slate-700 rounded-tl-none'
              }`}
            >
              <FormattedMessage content={msg.content} />

              {/* Show citations if available (only for model messages) */}
              {msg.role === 'model' && msg.citations && (
                <CitationsDisplay citations={msg.citations} />
              )}

              {/* ACTION CARD LOGIC */}
              {/* Check if the message contains actionable keywords like Task, Playbook, or email */}
              {msg.role === 'model' && (msg.content.includes('Task') || msg.content.includes('Playbook') || msg.content.includes('email') || isDoMode) && msg.content.length > 50 && (
                 <div className={`mt-4 p-3 rounded-lg border flex items-center gap-3 ${
                    isDoMode 
                      ? 'bg-emerald-950/40 border-emerald-900/50' // Success state in DO mode
                      : 'bg-blue-950/40 border-blue-900/50' // Proposal state in ASK mode
                 }`}>
                    {/* Icon */}
                    {isDoMode ? (
                       <CheckCircle className="w-5 h-5 flex-shrink-0 text-emerald-400" />
                    ) : (
                       <Layers className="w-5 h-5 flex-shrink-0 text-blue-400" />
                    )}
                    
                    {/* Text Content */}
                    <div className="flex-1">
                        <p className={`text-xs font-semibold ${isDoMode ? 'text-emerald-400' : 'text-blue-400'}`}>
                          {isDoMode ? 'EXECUTION SUCCESSFUL' : 'REMEDIATION PLAYBOOK IDENTIFIED'}
                        </p>
                        <p className="text-xs text-slate-400">
                          {isDoMode 
                             ? 'Playbook logic executed. Systems updated.' 
                             : 'This action is ready to be queued in the Execution Engine.'}
                        </p>
                    </div>

                    {/* Action Button (Only in ASK mode) */}
                    {!isDoMode && (
                      <button 
                        onClick={handleTransfer}
                        className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg transition-colors flex items-center gap-1 shadow-lg shadow-blue-900/20"
                      >
                        Execute <ArrowRight className="w-3 h-3" />
                      </button>
                    )}
                 </div>
              )}
            </div>
          </div>
        ))}
        
        {isTyping && (
           <div className="flex justify-start">
             <div className="bg-slate-800 p-4 rounded-2xl rounded-tl-none border border-slate-700 flex gap-2">
                <div className={`w-2 h-2 rounded-full animate-bounce ${isDoMode ? 'bg-emerald-500' : 'bg-slate-500'}`} style={{ animationDelay: '0ms' }} />
                <div className={`w-2 h-2 rounded-full animate-bounce ${isDoMode ? 'bg-emerald-500' : 'bg-slate-500'}`} style={{ animationDelay: '150ms' }} />
                <div className={`w-2 h-2 rounded-full animate-bounce ${isDoMode ? 'bg-emerald-500' : 'bg-slate-500'}`} style={{ animationDelay: '300ms' }} />
             </div>
           </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className={`p-4 bg-slate-900/90 border-t ${isDoMode ? 'border-emerald-900/30' : 'border-slate-800'}`}>
        <form onSubmit={handleSubmit} className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={placeholder}
            className={`w-full bg-slate-950 border text-slate-200 rounded-xl pl-4 pr-12 py-4 focus:outline-none focus:ring-1 transition-all placeholder:text-slate-600 shadow-inner ${
              isDoMode 
                ? 'border-emerald-900/50 focus:border-emerald-500 focus:ring-emerald-500' 
                : 'border-slate-700 focus:border-blue-500 focus:ring-blue-500'
            }`}
          />
          <button 
            type="submit"
            disabled={!input.trim() || isTyping}
            className={`absolute right-2 top-2 p-2 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg ${
              isDoMode 
                ? 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-900/20' 
                : 'bg-blue-600 hover:bg-blue-500 shadow-blue-900/20'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
};