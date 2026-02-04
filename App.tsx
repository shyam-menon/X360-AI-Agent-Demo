import React, { useEffect, useState } from 'react';
import { runMorningBriefing, sendChatMessage } from './services/backendService';
import { BriefingResponse, ChatMessage, ViewMode, BriefingItem } from './types';
import { RAW_CHAOTIC_DATA } from './constants';
import { Dashboard } from './components/Dashboard';
import { ChatInterface } from './components/ChatInterface';
import { DataViewer } from './components/DataViewer';
import { Layers, MessageSquare, Activity, Eye } from './components/Icons';

function App() {
  const [currentView, setCurrentView] = useState<ViewMode>('TELL');
  const [briefing, setBriefing] = useState<BriefingResponse | null>(null);
  const [isLoadingBriefing, setIsLoadingBriefing] = useState(true);
  
  // Split history state to keep contexts clear
  const [agentHistory, setAgentHistory] = useState<ChatMessage[]>([]); // For 'ASK' mode
  const [actionHistory, setActionHistory] = useState<ChatMessage[]>([]); // For 'DO' mode
  
  const [isChatTyping, setIsChatTyping] = useState(false);
  const [chatPrefill, setChatPrefill] = useState('');

  // The "Night Watchman": Runs on mount
  useEffect(() => {
    const init = async () => {
      // Run the API call and the animation timer in parallel
      // This ensures the animation shows for at least 800ms but doesn't delay the API call
      const minAnimationTime = new Promise(resolve => setTimeout(resolve, 800));
      const briefingRequest = runMorningBriefing(RAW_CHAOTIC_DATA);

      const [_, result] = await Promise.all([minAnimationTime, briefingRequest]);
      
      setBriefing(result);
      setIsLoadingBriefing(false);
    };
    init();
  }, []);

  const handleBriefingItemClick = (item: BriefingItem) => {
    // When clicking a briefing item, we go to AGENT (Ask) mode to analyze it
    setCurrentView('ASK');
    setChatPrefill(`What is the recommended playbook for the ${item.type.replace('_', ' ')} related to ${item.relatedTicketIds.join(', ')}?`);
    
    // Add context to Agent history
    setAgentHistory(prev => [
      ...prev, 
      { role: 'model', content: `I've opened the intelligence file for **${item.title}**.\n\nI can analyze the root cause or we can switch to **Actions** mode to execute a fix.`, timestamp: Date.now() }
    ]);
  };

  const handleSendMessage = async (msg: string) => {
    setIsChatTyping(true);
    
    // Determine which history to update
    const isDoMode = currentView === 'DO';
    const currentHistory = isDoMode ? actionHistory : agentHistory;
    const setHistory = isDoMode ? setActionHistory : setAgentHistory;

    // Optimistic update
    const newHistory = [...currentHistory, { role: 'user', content: msg, timestamp: Date.now() } as ChatMessage];
    setHistory(newHistory);

    // Get response - pass mode and context to backend
    const apiResponse = await sendChatMessage(
      newHistory,
      msg,
      isDoMode ? 'DO' : 'ASK',
      { data: RAW_CHAOTIC_DATA, briefing: briefing || undefined }
    );

    console.log('[CITATIONS DEBUG] API response:', {
      hasCitations: !!apiResponse.citations,
      citationsCount: apiResponse.citations?.length || 0,
      citations: apiResponse.citations
    });

    // Update with response
    setHistory(prev => [
      ...prev,
      {
        role: 'model',
        content: apiResponse.response,
        timestamp: Date.now(),
        citations: apiResponse.citations
      }
    ]);
    setIsChatTyping(false);
  };

  const handleRunAction = async (command: string) => {
    // 1. Switch View to DO
    setCurrentView('DO');
    
    // 2. Add the command to the Action History as if the user typed it
    const newHistory = [...actionHistory, { role: 'user', content: command, timestamp: Date.now() } as ChatMessage];
    setActionHistory(newHistory);
    setIsChatTyping(true);

    // 3. Trigger the response from the model in the Actions context
    const apiResponse = await sendChatMessage(
      newHistory,
      command,
      'DO',
      { data: RAW_CHAOTIC_DATA, briefing: briefing || undefined }
    );

    setActionHistory(prev => [
      ...prev,
      {
        role: 'model',
        content: apiResponse.response,
        timestamp: Date.now(),
        citations: apiResponse.citations
      }
    ]);
    setIsChatTyping(false);
  };

  const handleClearChat = () => {
    if (currentView === 'DO') {
        setActionHistory([]);
    } else {
        setAgentHistory([]);
    }
    setChatPrefill('');
  };

  const NavButton = ({ mode, icon: Icon, label }: { mode: ViewMode; icon: React.FC<any>; label: string }) => (
    <button
      onClick={() => setCurrentView(mode)}
      className={`flex flex-col items-center justify-center p-3 w-full transition-all duration-200 ${
        currentView === mode 
          ? 'text-white border-t-2 bg-slate-900' 
          : 'text-slate-500 hover:text-slate-300 hover:bg-slate-900/50'
      } ${currentView === mode && mode === 'DO' ? 'border-emerald-500 text-emerald-400' : currentView === mode ? 'border-blue-400 text-blue-400' : ''}`}
    >
      <Icon className={`w-6 h-6 mb-1 ${currentView === mode ? 'scale-110' : ''}`} />
      <span className="text-[10px] font-bold uppercase tracking-widest">{label}</span>
    </button>
  );

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-200 font-sans selection:bg-blue-500/30">
      
      {/* App Header */}
      <header className={`flex-none h-16 border-b bg-slate-950/80 backdrop-blur flex items-center px-6 sticky top-0 z-50 transition-colors duration-500 ${currentView === 'DO' ? 'border-emerald-900/50' : 'border-slate-800'}`}>
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center shadow-lg transition-colors duration-500 ${currentView === 'DO' ? 'bg-gradient-to-tr from-emerald-600 to-teal-400 shadow-emerald-900/20' : 'bg-gradient-to-tr from-blue-600 to-indigo-400 shadow-blue-900/20'}`}>
            <span className="font-bold text-white text-lg">X</span>
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-tight text-white leading-tight">X360 Agent</h1>
            <p className="text-[10px] text-slate-500 font-mono">V 1.0.4 • CONNECTED</p>
          </div>
        </div>
        <div className="ml-auto flex items-center gap-4">
            <span className={`hidden md:inline-flex items-center gap-2 px-3 py-1 rounded-full border text-xs transition-colors duration-500 ${currentView === 'DO' ? 'bg-emerald-950/30 border-emerald-900/50 text-emerald-400' : 'bg-slate-900 border-slate-800 text-slate-400'}`}>
                <span className={`w-2 h-2 rounded-full animate-pulse ${currentView === 'DO' ? 'bg-emerald-500' : 'bg-blue-500'}`}></span>
                {currentView === 'DO' ? 'Execution Mode' : 'System Nominal'}
            </span>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden relative">
        <div className="h-full overflow-y-auto px-4 py-6 md:px-8 max-w-7xl mx-auto scroll-smooth">
          
          {currentView === 'TELL' && (
            <Dashboard 
              data={briefing} 
              loading={isLoadingBriefing} 
              onItemClick={handleBriefingItemClick} 
            />
          )}

          {currentView === 'ASK' && (
            <ChatInterface 
              history={agentHistory} 
              onSendMessage={handleSendMessage} 
              isTyping={isChatTyping}
              prefill={chatPrefill}
              mode="ASK"
              onRunAction={handleRunAction}
              onClearChat={handleClearChat}
            />
          )}

          {currentView === 'DATA' && (
            <DataViewer data={RAW_CHAOTIC_DATA} />
          )}

          {currentView === 'DO' && (
             <ChatInterface 
                history={actionHistory}
                onSendMessage={handleSendMessage} 
                isTyping={isChatTyping}
                mode="DO"
                suggestedActions={briefing?.items || []}
                onClearChat={handleClearChat}
             />
          )}
        </div>
      </main>

      {/* Bottom Navigation (Mobile First / Sticky) */}
      <nav className={`flex-none h-20 bg-slate-950 border-t flex items-stretch justify-around z-50 pb-safe ${currentView === 'DO' ? 'border-emerald-900/30' : 'border-slate-800'}`}>
        <NavButton mode="TELL" icon={Activity} label="Dashboard" />
        <NavButton mode="ASK" icon={MessageSquare} label="Agent" />
        <NavButton mode="DO" icon={Layers} label="Actions" />
        <NavButton mode="DATA" icon={Eye} label="Raw Data" />
      </nav>

    </div>
  );
}

export default App;