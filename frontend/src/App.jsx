import { useState } from 'react'
import './App.css'
import AgentView from './components/AgentView'
import AdminView from './components/AdminView'
import SuperAdminView from './components/SuperAdminView'

function App() {
  const [currentRole, setCurrentRole] = useState('agent')

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🛡️ Compliance-First AI Content Generation</h1>
          <p className="subtitle">Industry-Grade Platform for Regulated Environments</p>
        </div>
        
        <div className="role-selector">
          <button
            className={`role-btn ${currentRole === 'agent' ? 'active' : ''}`}
            onClick={() => setCurrentRole('agent')}
          >
            👤 Agent
          </button>
          <button
            className={`role-btn ${currentRole === 'admin' ? 'active' : ''}`}
            onClick={() => setCurrentRole('admin')}
          >
            📊 Admin
          </button>
          <button
            className={`role-btn ${currentRole === 'super_admin' ? 'active' : ''}`}
            onClick={() => setCurrentRole('super_admin')}
          >
            ⚙️ Super Admin
          </button>
        </div>
      </header>

      <main className="app-main">
        {currentRole === 'agent' && <AgentView />}
        {currentRole === 'admin' && <AdminView />}
        {currentRole === 'super_admin' && <SuperAdminView />}
      </main>

      <footer className="app-footer">
        <p>Compliance-First AI Platform • Production-Grade POC • Fintech/Insurance Ready</p>
      </footer>
    </div>
  )
}

export default App
