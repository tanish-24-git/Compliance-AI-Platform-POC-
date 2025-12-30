import { Link } from 'react-router-dom';

export function HomePage() {
  return (
    <div style={{ 
      maxWidth: '1000px', 
      margin: '0 auto', 
      padding: '60px 20px',
      textAlign: 'center'
    }}>
      {/* Hero Section */}
      <div style={{ marginBottom: '60px' }}>
        <h1 style={{ 
          fontSize: '48px', 
          marginBottom: '24px',
          background: 'var(--gradient-bajaj)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          fontWeight: 800,
          letterSpacing: '-1px'
        }}>
          Bajaj Compliance AI
        </h1>
        <p style={{ 
          fontSize: '20px', 
          color: 'var(--text-secondary)',
          maxWidth: '600px',
          margin: '0 auto',
          lineHeight: 1.6
        }}>
          Generate compliant insurance content with AI-powered validation against IRDAI regulations
        </p>
      </div>

      {/* Feature Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '24px',
        marginBottom: '60px'
      }}>
        <Link to="/agent" style={{ textDecoration: 'none' }}>
          <div className="card" style={{ 
            height: '100%',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            background: 'var(--gradient-bajaj)',
            border: 'none',
            color: 'white'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>💬</div>
            <h3 style={{ fontSize: '24px', marginBottom: '12px', color: 'white' }}>Content Generation</h3>
            <p style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px' }}>
              Generate compliant insurance content with AI assistance
            </p>
          </div>
        </Link>

        <Link to="/admin" style={{ textDecoration: 'none' }}>
          <div className="card" style={{ 
            height: '100%',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
            <h3 style={{ fontSize: '24px', marginBottom: '12px' }}>Content Review</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              Review and approve generated content submissions
            </p>
          </div>
        </Link>

        <Link to="/super-admin" style={{ textDecoration: 'none' }}>
          <div className="card" style={{ 
            height: '100%',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚙️</div>
            <h3 style={{ fontSize: '24px', marginBottom: '12px' }}>Rule Management</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              Configure and manage compliance rules
            </p>
          </div>
        </Link>
      </div>

      {/* CTA Section */}
      <div className="card" style={{ 
        background: 'var(--bg-card)',
        padding: '40px',
        borderRadius: '20px'
      }}>
        <h2 style={{ fontSize: '32px', marginBottom: '16px' }}>Ready to get started?</h2>
        <p style={{ 
          fontSize: '16px', 
          color: 'var(--text-secondary)',
          marginBottom: '32px',
          maxWidth: '500px',
          margin: '0 auto 32px'
        }}>
          Experience the power of AI-driven compliance validation for insurance content
        </p>
        <Link to="/agent">
          <button className="btn btn-gold" style={{ 
            fontSize: '18px',
            padding: '16px 48px',
            fontWeight: 700
          }}>
            🚀 Start Generating Content
          </button>
        </Link>
      </div>

      {/* Stats Section */}
      <div style={{ 
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '32px',
        marginTop: '60px',
        padding: '40px 0'
      }}>
        <div>
          <div style={{ fontSize: '36px', fontWeight: 800, color: 'var(--accent-color)', marginBottom: '8px' }}>
            100%
          </div>
          <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
            Compliance Checked
          </div>
        </div>
        <div>
          <div style={{ fontSize: '36px', fontWeight: 800, color: 'var(--accent-color)', marginBottom: '8px' }}>
            Real-time
          </div>
          <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
            Validation
          </div>
        </div>
        <div>
          <div style={{ fontSize: '36px', fontWeight: 800, color: 'var(--accent-color)', marginBottom: '8px' }}>
            AI-Powered
          </div>
          <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
            Content Generation
          </div>
        </div>
      </div>
    </div>
  );
}
