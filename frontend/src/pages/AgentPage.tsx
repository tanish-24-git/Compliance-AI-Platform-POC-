import { useState } from 'react';
import { ChatInterface } from '../components/agent/ChatInterface';
import { DocumentUpload } from '../components/agent/DocumentUpload';

export function AgentPage() {
  const [showDocUpload, setShowDocUpload] = useState(false);

  return (
    <div style={{ position: 'relative' }}>
      {/* Main Chat Interface */}
      <ChatInterface />
      
      {/* Floating Action Button for Document Upload */}
      <button
        onClick={() => setShowDocUpload(!showDocUpload)}
        style={{
          position: 'fixed',
          bottom: '30px',
          right: '30px',
          width: '56px',
          height: '56px',
          borderRadius: '50%',
          background: 'var(--gradient-bajaj)',
          border: 'none',
          color: 'white',
          fontSize: '24px',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(0, 48, 135, 0.3)',
          transition: 'all 0.3s ease',
          zIndex: 1000,
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.1)';
          e.currentTarget.style.boxShadow = '0 6px 20px rgba(0, 48, 135, 0.4)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 48, 135, 0.3)';
        }}
        title="Upload Document for Compliance Check"
      >
        +
      </button>

      {/* Document Upload Modal */}
      {showDocUpload && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1001,
          }}
          onClick={() => setShowDocUpload(false)}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: 'var(--bg-card)',
              borderRadius: '16px',
              padding: '24px',
              maxWidth: '600px',
              width: '90%',
              maxHeight: '80vh',
              overflow: 'auto',
              boxShadow: 'var(--shadow-xl)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{ margin: 0 }}>Document Compliance Check</h2>
              <button
                onClick={() => setShowDocUpload(false)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  fontSize: '24px',
                  cursor: 'pointer',
                  color: 'var(--text-secondary)',
                }}
              >
                ×
              </button>
            </div>
            <DocumentUpload />
          </div>
        </div>
      )}
    </div>
  );
}
