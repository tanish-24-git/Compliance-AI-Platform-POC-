import { useState, useEffect } from 'react'
import axios from 'axios'
import '../App.css'

/**
 * Super Admin View - HUMAN-ONLY Rule Management
 * 
 * GOVERNANCE PRINCIPLES:
 * - Rules are written ONLY by humans (Super Admin)
 * - NO AI suggestions or auto-generation
 * - Documents are REFERENCE ONLY
 * - PostgreSQL is source of truth
 * - Pinecone stores derived embeddings only
 */

function SuperAdminView() {
  const [userId] = useState(3) // Super Admin user ID from seed
  const [rules, setRules] = useState([])
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [similarityWarning, setSimilarityWarning] = useState(null)
  
  // Form state
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [showDocuments, setShowDocuments] = useState(false)
  const [newRule, setNewRule] = useState({ 
    rule_text: '', 
    severity: 'hard',
    source_document_reference: ''
  })
  const [editingRule, setEditingRule] = useState(null)
  const [updateText, setUpdateText] = useState('')

  useEffect(() => {
    loadRules()
    loadDocuments()
  }, [])

  const loadRules = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await axios.get('/api/super-admin/rules?include_inactive=true')
      setRules(response.data.rules || [])
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load rules')
    } finally {
      setLoading(false)
    }
  }

  const loadDocuments = async () => {
    try {
      const response = await axios.get('/api/super-admin/documents')
      setDocuments(response.data.documents || [])
    } catch (err) {
      console.error('Failed to load documents:', err)
    }
  }

  const handleCreateRule = async (e) => {
    e.preventDefault()
    
    // Validate HUMAN input
    if (!newRule.rule_text.trim()) {
      setError('Rule text is required and must be manually entered by you')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)
    setSimilarityWarning(null)

    try {
      const response = await axios.post('/api/super-admin/rules', {
        rule_text: newRule.rule_text,
        severity: newRule.severity,
        created_by: userId,
        source_document_reference: newRule.source_document_reference || null
      })

      if (response.data.status === 'warning') {
        // Similar rules found - show warning
        setSimilarityWarning(response.data)
        setLoading(false)
        return
      }

      setSuccess('Rule created successfully! (Human-defined)')
      setNewRule({ rule_text: '', severity: 'hard', source_document_reference: '' })
      setShowCreateForm(false)
      loadRules()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create rule')
    } finally {
      setLoading(false)
    }
  }

  const handleForceCreate = async () => {
    setLoading(true)
    setError(null)
    setSimilarityWarning(null)

    try {
      await axios.post('/api/super-admin/rules/force-create', {
        rule_text: newRule.rule_text,
        severity: newRule.severity,
        created_by: userId,
        source_document_reference: newRule.source_document_reference || null
      })

      setSuccess('Rule created successfully! (Confirmed distinct by you)')
      setNewRule({ rule_text: '', severity: 'hard', source_document_reference: '' })
      setShowCreateForm(false)
      loadRules()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create rule')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateRule = async (ruleId) => {
    // Validate HUMAN input
    if (!updateText.trim()) {
      setError('Updated rule text is required and must be manually entered by you')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      await axios.put(`/api/super-admin/rules/${ruleId}?user_id=${userId}`, {
        rule_text: updateText
      })

      setSuccess('Rule updated successfully! New version created. (Human-edited)')
      setEditingRule(null)
      setUpdateText('')
      loadRules()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update rule')
    } finally {
      setLoading(false)
    }
  }

  const handleDeactivateRule = async (ruleId) => {
    if (!window.confirm('Are you sure you want to deactivate this rule?')) {
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      await axios.delete(`/api/super-admin/rules/${ruleId}?user_id=${userId}`)
      setSuccess('Rule deactivated successfully! (Human decision)')
      loadRules()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to deactivate rule')
    } finally {
      setLoading(false)
    }
  }

  const handleDocumentUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)
    formData.append('user_id', userId)

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post('/api/super-admin/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      setSuccess(response.data.message + ' - ' + response.data.note)
      loadDocuments()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload document')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <div className="view-container">
      <h2 className="view-title">⚙️ Super Admin - HUMAN-ONLY Rule Management</h2>
      
      <div className="alert alert-info" style={{ marginBottom: '1.5rem' }}>
        <span>ℹ️</span>
        <div>
          <strong>Governance Principle:</strong> Rules are created ONLY by humans (you). 
          NO AI suggestions. Documents are reference material only. You manually write all rules.
        </div>
      </div>

      <div style={{ marginBottom: '2rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <button
          className="btn btn-primary"
          onClick={() => {
            setShowCreateForm(!showCreateForm)
            setShowDocuments(false)
          }}
        >
          {showCreateForm ? '❌ Cancel' : '➕ Create New Rule (Manual)'}
        </button>
        <button
          className="btn btn-secondary"
          onClick={() => {
            setShowDocuments(!showDocuments)
            setShowCreateForm(false)
          }}
        >
          📄 Reference Documents ({documents.length})
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          <span>❌</span>
          <div>{error}</div>
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <span>✅</span>
          <div>{success}</div>
        </div>
      )}

      {similarityWarning && (
        <div className="card" style={{ marginBottom: '2rem', background: '#fef3c7', borderLeft: '4px solid #f59e0b' }}>
          <h3 style={{ marginBottom: '1rem', color: '#92400e' }}>⚠️ Similar Rules Found</h3>
          <p style={{ marginBottom: '1rem' }}>{similarityWarning.message}</p>
          
          <div style={{ marginBottom: '1rem' }}>
            {similarityWarning.similar_rules.map((similar, idx) => (
              <div key={idx} style={{ 
                background: 'white', 
                padding: '0.75rem', 
                borderRadius: '6px', 
                marginBottom: '0.5rem' 
              }}>
                <div style={{ fontSize: '0.9rem', marginBottom: '0.25rem' }}>
                  <strong>Rule #{similar.rule_id}</strong> - {(similar.similarity_score * 100).toFixed(1)}% similar
                </div>
                <div style={{ fontSize: '0.85rem', color: '#4b5563' }}>{similar.rule_text}</div>
              </div>
            ))}
          </div>

          <p style={{ fontSize: '0.9rem', marginBottom: '1rem', color: '#92400e' }}>
            <strong>Your decision:</strong> Review the similarities above. If your rule is distinct, click "Create Anyway".
          </p>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className="btn btn-primary"
              onClick={handleForceCreate}
              disabled={loading}
            >
              ✓ Create Anyway (I confirm it's distinct)
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => setSimilarityWarning(null)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {showDocuments && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>📄 Reference Documents (For Human Review Only)</h3>
          
          <div className="alert alert-warning" style={{ marginBottom: '1rem' }}>
            <span>⚠️</span>
            <div>
              These documents are <strong>reference material only</strong>. 
              NO rules will be auto-generated. You must read and manually write rules.
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Upload Reference Document</label>
            <input
              type="file"
              className="file-input"
              onChange={handleDocumentUpload}
              accept=".pdf,.docx,.md"
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#718096' }}>
              Supported: PDF, DOCX, Markdown - For your reference only
            </p>
          </div>

          {documents.length > 0 ? (
            <div style={{ marginTop: '1rem' }}>
              <h4 style={{ marginBottom: '0.75rem', fontSize: '1rem' }}>Uploaded Documents:</h4>
              {documents.map((doc, idx) => (
                <div key={idx} className="card" style={{ padding: '0.75rem', marginBottom: '0.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: '600' }}>{doc.filename}</div>
                      <div style={{ fontSize: '0.85rem', color: '#718096' }}>
                        {formatFileSize(doc.size_bytes)} • {doc.purpose}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#718096', fontStyle: 'italic', marginTop: '1rem' }}>
              No reference documents uploaded yet
            </p>
          )}
        </div>
      )}

      {showCreateForm && !similarityWarning && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>✍️ Create New Compliance Rule (Manual Entry)</h3>
          
          <div className="alert alert-warning" style={{ marginBottom: '1rem' }}>
            <span>✋</span>
            <div>
              <strong>HUMAN-ONLY:</strong> You must manually type the rule text below. 
              NO AI assistance. NO auto-generation from documents.
            </div>
          </div>

          <form onSubmit={handleCreateRule}>
            <div className="form-group">
              <label className="form-label">Rule Text * (Type manually)</label>
              <textarea
                className="form-textarea"
                value={newRule.rule_text}
                onChange={(e) => setNewRule({ ...newRule, rule_text: e.target.value })}
                placeholder='Example: Content must not include "guaranteed returns" or "risk-free"'
                rows="4"
                required
              />
              <p style={{ fontSize: '0.85rem', color: '#718096', marginTop: '0.25rem' }}>
                Type the complete rule text yourself. Be specific and clear.
              </p>
            </div>

            <div className="form-group">
              <label className="form-label">Severity *</label>
              <select
                className="form-input"
                value={newRule.severity}
                onChange={(e) => setNewRule({ ...newRule, severity: e.target.value })}
              >
                <option value="hard">HARD - Violations block content</option>
                <option value="soft">SOFT - Violations are flagged only</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Source Document Reference (Optional)</label>
              <select
                className="form-input"
                value={newRule.source_document_reference}
                onChange={(e) => setNewRule({ ...newRule, source_document_reference: e.target.value })}
              >
                <option value="">None</option>
                {documents.map((doc, idx) => (
                  <option key={idx} value={doc.filename}>{doc.filename}</option>
                ))}
              </select>
              <p style={{ fontSize: '0.85rem', color: '#718096', marginTop: '0.25rem' }}>
                Optional: Link to reference document you reviewed
              </p>
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : '✓ Save Rule (Human-Created)'}
            </button>
          </form>
        </div>
      )}

      {!loading && !showCreateForm && !showDocuments && (
        <div>
          <h3 style={{ marginBottom: '1rem', color: '#2d3748' }}>
            All Rules ({rules.length}) - Human-Created Only
          </h3>
          
          {rules.length === 0 ? (
            <div className="alert alert-info">
              <span>ℹ️</span>
              <div>No rules found. Create your first compliance rule manually!</div>
            </div>
          ) : (
            rules.map((rule) => (
              <div key={rule.id} className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                      <span className="badge badge-info">ID: {rule.id}</span>
                      <span className={`badge ${rule.severity === 'hard' ? 'badge-danger' : 'badge-warning'}`}>
                        {rule.severity.toUpperCase()}
                      </span>
                      <span className={`badge ${rule.is_active ? 'badge-success' : 'badge-danger'}`}>
                        {rule.is_active ? 'ACTIVE' : 'INACTIVE'}
                      </span>
                      <span className="badge badge-info">v{rule.version}</span>
                      <span className="badge badge-success">👤 Human-Created</span>
                      {rule.parent_rule_id && (
                        <span className="badge badge-warning">
                          Updated from #{rule.parent_rule_id}
                        </span>
                      )}
                    </div>
                    
                    {editingRule === rule.id ? (
                      <div style={{ marginTop: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                          Edit Rule Text (Manual):
                        </label>
                        <textarea
                          className="form-textarea"
                          value={updateText}
                          onChange={(e) => setUpdateText(e.target.value)}
                          rows="3"
                        />
                        <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem' }}>
                          <button
                            className="btn btn-primary"
                            onClick={() => handleUpdateRule(rule.id)}
                            disabled={loading}
                          >
                            ✓ Save Update (Human-Edited)
                          </button>
                          <button
                            className="btn btn-secondary"
                            onClick={() => {
                              setEditingRule(null)
                              setUpdateText('')
                            }}
                          >
                            Cancel
                          </button>
                        </div>
                        <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#718096' }}>
                          Note: Updating creates a new version and deactivates the old one
                        </p>
                      </div>
                    ) : (
                      <p style={{ marginTop: '0.5rem', lineHeight: '1.6', color: '#2d3748' }}>
                        {rule.rule_text}
                      </p>
                    )}
                  </div>
                  
                  {rule.is_active && editingRule !== rule.id && (
                    <div style={{ display: 'flex', gap: '0.5rem', marginLeft: '1rem' }}>
                      <button
                        className="btn btn-secondary"
                        onClick={() => {
                          setEditingRule(rule.id)
                          setUpdateText(rule.rule_text)
                        }}
                        style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                      >
                        ✏️ Edit
                      </button>
                      <button
                        className="btn btn-danger"
                        onClick={() => handleDeactivateRule(rule.id)}
                        style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                      >
                        🗑️ Deactivate
                      </button>
                    </div>
                  )}
                </div>
                
                <div style={{ fontSize: '0.85rem', color: '#718096', marginTop: '0.5rem' }}>
                  Created by User {rule.created_by} • {formatDate(rule.created_at)} • Source: {rule.source}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {loading && !showCreateForm && !showDocuments && (
        <div className="loading">
          <div className="spinner"></div>
        </div>
      )}
    </div>
  )
}

export default SuperAdminView
