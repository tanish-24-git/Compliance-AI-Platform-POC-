import { useState, useEffect } from 'react'
import axios from 'axios'
import '../App.css'

function AdminView() {
  const [activeTab, setActiveTab] = useState('violations')
  const [violations, setViolations] = useState([])
  const [submissions, setSubmissions] = useState([])
  const [analytics, setAnalytics] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadData()
  }, [activeTab])

  const loadData = async () => {
    setLoading(true)
    setError(null)

    try {
      if (activeTab === 'violations') {
        const response = await axios.get('/api/violations')
        setViolations(response.data.violations || [])
      } else if (activeTab === 'submissions') {
        const response = await axios.get('/api/submissions')
        setSubmissions(response.data.submissions || [])
      } else if (activeTab === 'analytics') {
        const response = await axios.get('/api/analytics/rules')
        setAnalytics(response.data.rule_analytics || [])
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="view-container">
      <h2 className="view-title">📊 Admin View - Compliance Monitoring</h2>
      
      <div style={{ marginBottom: '2rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <button
          className={`btn ${activeTab === 'violations' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('violations')}
        >
          ⚠️ Violations
        </button>
        <button
          className={`btn ${activeTab === 'submissions' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('submissions')}
        >
          📝 Submissions
        </button>
        <button
          className={`btn ${activeTab === 'analytics' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('analytics')}
        >
          📈 Rule Analytics
        </button>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          <span>❌</span>
          <div>{error}</div>
        </div>
      )}

      {!loading && !error && (
        <>
          {activeTab === 'violations' && (
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Submission</th>
                    <th>User</th>
                    <th>Rule</th>
                    <th>Severity</th>
                    <th>Violated Text</th>
                    <th>Context</th>
                    <th>Detected At</th>
                  </tr>
                </thead>
                <tbody>
                  {violations.length === 0 ? (
                    <tr>
                      <td colSpan="8" style={{ textAlign: 'center', padding: '2rem', color: '#718096' }}>
                        No violations found
                      </td>
                    </tr>
                  ) : (
                    violations.map((v) => (
                      <tr key={v.id}>
                        <td>{v.id}</td>
                        <td>#{v.submission_id}</td>
                        <td>User {v.user_id}</td>
                        <td style={{ maxWidth: '300px', fontSize: '0.9rem' }}>{v.rule_text}</td>
                        <td>
                          <span className={`badge ${v.severity === 'hard' ? 'badge-danger' : 'badge-warning'}`}>
                            {v.severity.toUpperCase()}
                          </span>
                        </td>
                        <td style={{ maxWidth: '200px', fontSize: '0.85rem', fontStyle: 'italic' }}>
                          {v.violated_text || 'N/A'}
                        </td>
                        <td style={{ maxWidth: '250px', fontSize: '0.85rem' }}>{v.context}</td>
                        <td style={{ fontSize: '0.85rem' }}>{formatDate(v.detected_at)}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'submissions' && (
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>User</th>
                    <th>Prompt</th>
                    <th>Status</th>
                    <th>Compliance</th>
                    <th>Violations</th>
                    <th>Created At</th>
                  </tr>
                </thead>
                <tbody>
                  {submissions.length === 0 ? (
                    <tr>
                      <td colSpan="7" style={{ textAlign: 'center', padding: '2rem', color: '#718096' }}>
                        No submissions found
                      </td>
                    </tr>
                  ) : (
                    submissions.map((s) => (
                      <tr key={s.id}>
                        <td>{s.id}</td>
                        <td>User {s.user_id}</td>
                        <td style={{ maxWidth: '300px', fontSize: '0.9rem' }}>{s.prompt}</td>
                        <td>
                          <span className={`badge badge-info`}>
                            {s.status.toUpperCase()}
                          </span>
                        </td>
                        <td>
                          <span className={`badge ${s.compliance_status === 'approved' ? 'badge-success' : 'badge-danger'}`}>
                            {s.compliance_status ? s.compliance_status.toUpperCase() : 'PENDING'}
                          </span>
                        </td>
                        <td>
                          <span className="badge badge-warning">
                            {s.violation_count}
                          </span>
                        </td>
                        <td style={{ fontSize: '0.85rem' }}>{formatDate(s.created_at)}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div>
              <div style={{ marginBottom: '1rem', color: '#4a5568' }}>
                <strong>Rule Hit Frequency</strong> - Shows which rules are violated most often
              </div>
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Rule ID</th>
                      <th>Rule Text</th>
                      <th>Severity</th>
                      <th>Violation Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.length === 0 ? (
                      <tr>
                        <td colSpan="4" style={{ textAlign: 'center', padding: '2rem', color: '#718096' }}>
                          No analytics data available
                        </td>
                      </tr>
                    ) : (
                      analytics.map((a) => (
                        <tr key={a.rule_id}>
                          <td>{a.rule_id}</td>
                          <td style={{ maxWidth: '400px' }}>{a.rule_text}</td>
                          <td>
                            <span className={`badge ${a.severity === 'hard' ? 'badge-danger' : 'badge-warning'}`}>
                              {a.severity.toUpperCase()}
                            </span>
                          </td>
                          <td>
                            <span style={{ 
                              fontSize: '1.2rem', 
                              fontWeight: '700',
                              color: a.violation_count > 0 ? '#e53e3e' : '#38a169'
                            }}>
                              {a.violation_count}
                            </span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default AdminView
