import React, { useState } from 'react';

function App() {
  const [port, setPort] = useState('4000');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeAgents, setActiveAgents] = useState([]);

  const agents = port === '4000' ? [
    { id: 'lead', name: 'Event Lead Agent', role: 'Supervisor & Coordinator', status: 'online' },
    { id: 'sponsor', name: 'Sponsorship Agent', role: 'Sponsor Tiers & Packages', status: 'online' },
    { id: 'marketing', name: 'Marketing Agent', role: 'Promo & Social Media', status: 'online' },
    { id: 'venue', name: 'Venue Agent', role: 'Logistics & Rooms', status: 'online' },
    { id: 'catering', name: 'Catering Agent', role: 'Food & Dietary', status: 'offline' } // Missing for Session 1 Lab!
  ] : [
    { id: 'lead', name: 'Event Lead Agent', role: 'Supervisor & Coordinator', status: 'online' },
    { id: 'sponsor', name: 'Sponsorship Agent', role: 'Sponsor Tiers & Packages', status: 'online' },
    { id: 'marketing', name: 'Marketing Agent', role: 'Promo & Social Media', status: 'online' },
    { id: 'catering', name: 'Catering Agent', role: 'Food & Dietary', status: 'online' },
    { id: 'venue', name: 'Venue Agent', role: 'Logistics & Rooms', status: 'offline' }     // Missing for Session 2 Lab!
  ];

  const samplePrompts = [
    "What perks come with the Gold sponsorship tier?",
    "Draft a Twitter announcement post for our AI Hackathon.",
    "What is the capacity and equipment in the Main Stage Hall?",
    "Can you estimate catering and meals for 100 people?"
  ];

  const handleChipClick = (promptText) => {
    setInput(promptText);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setActiveAgents(['lead']); // Lead always starts processing

    try {
      const response = await fetch(`http://localhost:${port}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, sessionId: 'user-123' }),
      });
      const data = await response.json();
      
      if (data.activeAgents) {
        setActiveAgents(data.activeAgents);
      }

      const agentMsg = { 
        role: 'system', 
        content: data.reply, 
        traces: data.traces || [], 
        framework: data.framework 
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [...prev, { role: 'system', content: 'Error connecting to the backend. Is it running?', traces: [] }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="header">
        <h1>Event<span className="header-brand">Craft</span> AI</h1>
        <select value={port} onChange={(e) => setPort(e.target.value)}>
          <option value="4000">🚀 Backend: LangChain (Port 4000)</option>
          <option value="4001">🧠 Backend: Google ADK (Port 4001)</option>
        </select>
      </header>

      <div className="workspace">
        <aside className="sidebar">
          <h3>Agent Team</h3>
          {agents.map(agent => {
            const isWorking = activeAgents.includes(agent.id);
            const isOffline = agent.status === 'offline';
            return (
              <div key={agent.id} className={`agent-card ${isWorking ? 'active' : ''} ${isOffline ? 'offline' : ''}`}>
                <div className="agent-name">{agent.name}</div>
                <div className="agent-role">{agent.role}</div>
                <div className={`agent-status ${isWorking ? 'status-active' : isOffline ? 'status-offline' : 'status-idle'}`}>
                  {isOffline ? 'Missing (Lab Step)' : isWorking ? (loading ? 'Working...' : 'Invoked') : 'Idle'}
                </div>
              </div>
            );
          })}
        </aside>

        <main className="main-content">
          <div className="chat-container">
            {messages.length === 0 && (
              <div className="message-wrapper system">
                <div className="sender-name">Event Lead Agent</div>
                <div className="message">
                  Hello! I'm the Event Lead. My team of specialized agents and I are here to help organize your event. What do you need assistance with?
                </div>
              </div>
            )}
            
            {messages.map((m, idx) => (
              <div key={idx} className={`message-wrapper ${m.role}`}>
                <div className="sender-header">
                  <span className="sender-avatar">{m.role === 'user' ? '👤' : '🤖'}</span>
                  <span className="sender-name">
                    {m.role === 'user' ? 'You' : `Event Team (${m.framework || 'System'})`}
                  </span>
                </div>
                
                <div className="message-card">
                  {m.traces && m.traces.length > 0 && (
                    <details className="trace-details" open>
                      <summary className="trace-summary">
                        ⚙️ System Trace ({m.traces.length} steps)
                      </summary>
                      <ul className="trace-list">
                        {m.traces.map((t, i) => (
                          <li key={i} className={`trace-item ${t.includes('❌') || t.includes('Error') ? 'error' : ''}`}>
                            {t}
                          </li>
                        ))}
                      </ul>
                    </details>
                  )}
                  
                  <div className="message-content">{m.content}</div>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="message-wrapper system">
                <div className="sender-name">System</div>
                <div className="message" style={{ opacity: 0.7 }}>
                  Agents are coordinating...
                </div>
              </div>
            )}
          </div>

          <div className="examples-container">
            <span className="examples-label">Try an example:</span>
            {samplePrompts.map((promptText, index) => (
              <button 
                key={index} 
                className="example-chip" 
                onClick={() => handleChipClick(promptText)}
                disabled={loading}
              >
                {promptText}
              </button>
            ))}
          </div>

          <div className="input-area">
            <input 
              type="text" 
              value={input} 
              onChange={(e) => setInput(e.target.value)} 
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="e.g. Plan sponsorships and write a promo tweet..."
            />
            <button onClick={sendMessage} disabled={loading}>Send</button>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
