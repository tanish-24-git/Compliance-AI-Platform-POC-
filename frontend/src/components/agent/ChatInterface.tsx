import React, { useState, useEffect, useRef } from 'react';
import { agentAPI } from '../../services/api';
import type { GenerateContentResponse } from '../../types';

const MOCK_USER_ID = '00000000-0000-0000-0000-000000000001';

const QUICK_PROMPTS = [
  'Generate Term Insurance description',
  'Create Health Plan content',
  'Write Car Policy details',
];

interface Message {
  role: 'user' | 'system';
  content: string;
  data?: GenerateContentResponse;
  timestamp: Date;
}

// Component to format content professionally
const FormattedContent = ({ content }: { content: string }) => {
  const formatText = (text: string) => {
    // Split by double newlines for paragraphs
    const paragraphs = text.split('\n\n');
    
    return paragraphs.map((para, idx) => {
      // Check if it's a bullet point list
      if (para.includes('\n-') || para.includes('\n•') || para.includes('\n*')) {
        const lines = para.split('\n');
        const items = lines.filter(line => line.trim().match(/^[-•*]/));
        
        if (items.length > 0) {
          return (
            <ul key={idx} style={{ marginBottom: '16px', paddingLeft: '24px', lineHeight: '1.8' }}>
              {items.map((item, i) => (
                <li key={i} style={{ marginBottom: '8px' }}>
                  {item.replace(/^[-•*]\s*/, '')}
                </li>
              ))}
            </ul>
          );
        }
      }
      
      // Check if it's a numbered list
      if (para.match(/^\d+\./m)) {
        const lines = para.split('\n');
        const items = lines.filter(line => line.trim().match(/^\d+\./));
        
        if (items.length > 0) {
          return (
            <ol key={idx} style={{ marginBottom: '16px', paddingLeft: '24px', lineHeight: '1.8' }}>
              {items.map((item, i) => (
                <li key={i} style={{ marginBottom: '8px' }}>
                  {item.replace(/^\d+\.\s*/, '')}
                </li>
              ))}
            </ol>
          );
        }
      }
      
      // Check if it's a heading (starts with ** or #)
      if (para.trim().startsWith('**') && para.trim().endsWith('**')) {
        const heading = para.replace(/\*\*/g, '');
        return (
          <h3 key={idx} style={{ 
            marginTop: '20px', 
            marginBottom: '12px', 
            fontWeight: 700,
            fontSize: '16px',
            color: 'var(--accent-color)'
          }}>
            {heading}
          </h3>
        );
      }
      
      if (para.trim().startsWith('#')) {
        const heading = para.replace(/^#+\s*/, '');
        return (
          <h3 key={idx} style={{ 
            marginTop: '20px', 
            marginBottom: '12px', 
            fontWeight: 700,
            fontSize: '16px',
            color: 'var(--accent-color)'
          }}>
            {heading}
          </h3>
        );
      }
      
      // Regular paragraph
      if (para.trim()) {
        return (
          <p key={idx} style={{ marginBottom: '12px', lineHeight: '1.7' }}>
            {para}
          </p>
        );
      }
      
      return null;
    });
  };

  return <div style={{ fontSize: '14px' }}>{formatText(content)}</div>;
};

export function ChatInterface() {
  const [prompt, setPrompt] = useState('');
  const [useEnhancer, setUseEnhancer] = useState(false);
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleGenerate = async (customPrompt?: string) => {
    const promptText = customPrompt || prompt;
    
    if (!promptText.trim() || promptText.length < 5) {
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: 'Error: Prompt must be at least 5 characters long.',
        timestamp: new Date()
      }]);
      return;
    }

    setLoading(true);
    
    // Add user message
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: promptText,
      timestamp: new Date()
    }]);

    try {
      const response = await agentAPI.generateContent({
        prompt: promptText,
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
          timestamp: new Date()
        },
      ]);

      setPrompt('');
    } catch (error: any) {
      let errorMessage = 'An error occurred';
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMessage = detail
            .map((err: any) => `${err.loc[err.loc.length - 1]}: ${err.msg}`)
            .join(', ');
        } else {
          errorMessage = String(detail);
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setMessages(prev => [
        ...prev,
        {
          role: 'system',
          content: `Error: ${errorMessage}`,
          timestamp: new Date()
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickPrompt = (quickPrompt: string) => {
    setPrompt(quickPrompt);
    handleGenerate(quickPrompt);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleGenerate();
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Content copied to clipboard!');
  };

  const regenerateContent = (originalPrompt: string) => {
    handleGenerate(originalPrompt);
  };

  return (
    <div className="card" style={{ padding: 0 }}>
      <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-color)' }}>
        <h2 style={{ margin: 0 }}>Content Generation</h2>
      </div>

      {/* Quick Prompts */}
      {messages.length === 0 && (
        <div className="quick-prompts">
          <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-secondary)' }}>
            Quick Actions:
          </span>
          {QUICK_PROMPTS.map((qp, idx) => (
            <button
              key={idx}
              className="quick-prompt-chip"
              onClick={() => handleQuickPrompt(qp)}
              disabled={loading}
            >
              {qp}
            </button>
          ))}
        </div>
      )}

      <div className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="empty-state">
              <div className="empty-state-icon">💬</div>
              <h3>Welcome to Bajaj Compliance AI</h3>
              <p>Start a conversation to generate compliant insurance content</p>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`message message-${msg.role}`}>
              {/* Use formatted content for system messages, plain for user */}
              {msg.role === 'system' && !msg.content.startsWith('Error:') ? (
                <FormattedContent content={msg.content} />
              ) : (
                <div>{msg.content}</div>
              )}
              
              {/* Compliance Status & Actions */}
              {msg.data && (
                <div style={{ marginTop: '16px' }}>
                  {/* Status Badge */}
                  <div style={{ marginBottom: '12px' }}>
                    <span className={`status-badge ${msg.data.compliance_status.toLowerCase()}`}>
                      {msg.data.compliance_status === 'compliant' ? '✓' : '⚠'}
                      {' '}
                      {msg.data.compliance_status.toUpperCase()}
                    </span>
                  </div>

                  {/* Rule Violations */}
                  {msg.data.rules_triggered.length > 0 && (
                    <div className="violation-card">
                      <div className="violation-header">
                        <span className="violation-icon">⚠</span>
                        <strong style={{ fontSize: '14px' }}>
                          {msg.data.rules_triggered.length} Rule(s) Triggered
                        </strong>
                      </div>
                      
                      <ul className="rule-list" style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        {msg.data.rules_triggered.map((rule, rIdx) => (
                          <li key={rIdx} className="rule-item">
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: '8px' }}>
                              <span style={{ flex: 1 }}>
                                {rule.rule_text.substring(0, 80)}...
                              </span>
                              <span className={`severity-badge severity-${rule.severity.toLowerCase()}`}>
                                {rule.severity}
                              </span>
                            </div>
                          </li>
                        ))}
                      </ul>

                      {msg.data.rules_triggered.filter(r => r.status === 'violated').length > 0 && (
                        <div style={{ 
                          marginTop: '12px', 
                          padding: '8px 12px', 
                          background: 'rgba(220, 53, 69, 0.1)',
                          borderRadius: '8px',
                          fontSize: '12px',
                          color: 'var(--error-color)',
                          fontWeight: 600
                        }}>
                          {msg.data.rules_triggered.filter(r => r.status === 'violated').length} Violation(s) Detected
                        </div>
                      )}
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="message-actions">
                    <button 
                      className="btn btn-outline"
                      onClick={() => copyToClipboard(msg.content)}
                      style={{ fontSize: '12px', padding: '6px 12px' }}
                    >
                      Copy
                    </button>
                    <button 
                      className="btn btn-outline"
                      onClick={() => {
                        const userMsg = messages[idx - 1];
                        if (userMsg?.role === 'user') {
                          regenerateContent(userMsg.content);
                        }
                      }}
                      style={{ fontSize: '12px', padding: '6px 12px' }}
                      disabled={loading}
                    >
                      Regenerate
                    </button>
                    {msg.data.compliance_status === 'compliant' && (
                      <button 
                        className="btn btn-success"
                        style={{ fontSize: '12px', padding: '6px 12px' }}
                      >
                        Approve
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
          
          {/* Typing Indicator */}
          {loading && (
            <div className="message message-system">
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
                <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                  Generating compliant content...
                </span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Container */}
        <div className="chat-input-container">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px' }}>
              <input
                type="checkbox"
                checked={useEnhancer}
                onChange={(e) => setUseEnhancer(e.target.checked)}
                style={{ cursor: 'pointer' }}
              />
              <span>Use Prompt Enhancer</span>
            </label>
          </div>
          
          <div className="chat-input-wrapper">
            <textarea
              className="textarea"
              placeholder="Type your insurance content prompt here..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
              style={{ minHeight: '56px', maxHeight: '150px' }}
            />
            <button
              className="btn btn-primary"
              onClick={() => handleGenerate()}
              disabled={loading || !prompt.trim()}
            >
              {loading ? 'Generating...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
