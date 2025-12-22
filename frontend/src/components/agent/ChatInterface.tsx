import React, { useState } from 'react';
import { agentAPI } from '../../services/api';
import type { GenerateContentResponse } from '../../types';

const MOCK_USER_ID = '00000000-0000-0000-0000-000000000001'; // Valid UUID for POC

export function ChatInterface() {
  const [prompt, setPrompt] = useState('');
  const [useEnhancer, setUseEnhancer] = useState(false);
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'system'; content: string; data?: GenerateContentResponse }>>([]);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: prompt }]);

    try {
      const response = await agentAPI.generateContent({
        prompt,
        use_prompt_enhancer: useEnhancer,
        user_id: MOCK_USER_ID,
      });

      // Add system response
      setMessages(prev => [
        ...prev,
        {
          role: 'system',
          content: response.final_content,
          data: response,
        },
      ]);

      setPrompt('');
    } catch (error: any) {
      let errorMessage = 'An error occurred';
      
      if (error.response?.data?.detail) {
        // FastAPI validation errors are arrays of objects
        if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail
            .map((err: any) => `${err.loc.join('.')}: ${err.msg}`)
            .join(', ');
        } else {
          errorMessage = error.response.data.detail;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setMessages(prev => [
        ...prev,
        {
          role: 'system',
          content: `Error: ${errorMessage}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleGenerate();
    }
  };

  return (
    <div className="card">
      <h2>Content Generation</h2>
      <div className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
              Start a conversation to generate compliant content
            </div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className={`message message-${msg.role}`}>
              {msg.content}
              {msg.data && (
                <div style={{ marginTop: '10px', fontSize: '12px' }}>
                  <div>
                    Status:{' '}
                    <span className={`status-${msg.data.compliance_status}`}>
                      {msg.data.compliance_status.toUpperCase()}
                    </span>
                  </div>
                  {msg.data.rules_triggered.length > 0 && (
                    <div style={{ marginTop: '5px' }}>
                      Rules: {msg.data.rules_triggered.length} triggered
                      {msg.data.rules_triggered.filter(r => r.status === 'violated').length > 0 && (
                        <span style={{ color: 'var(--error-color)' }}>
                          {' '}({msg.data.rules_triggered.filter(r => r.status === 'violated').length} violations)
                        </span>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="message message-system">
              <div className="loading"></div> Generating content...
            </div>
          )}
        </div>
        <div className="chat-input-container">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={useEnhancer}
                onChange={(e) => setUseEnhancer(e.target.checked)}
              />
              Use Prompt Enhancer
            </label>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <textarea
              className="textarea"
              placeholder="Enter your prompt here..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={handleKeyPress}
              style={{ minHeight: '60px' }}
              disabled={loading}
            />
            <button
              className="btn btn-primary"
              onClick={handleGenerate}
              disabled={loading || !prompt.trim()}
            >
              Generate
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
