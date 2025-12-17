import { useState } from 'react'
import axios from 'axios'
import '../App.css'

function AgentView() {
  const [userId] = useState(1) // Agent user ID from seed
  const [prompt, setPrompt] = useState('')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      // Validate file type
      const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/markdown']
      const allowedExtensions = ['.pdf', '.docx', '.md']
      const fileExtension = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase()
      
      if (allowedExtensions.includes(fileExtension)) {
        setFile(selectedFile)
        setError(null)
      } else {
        setError('Please upload a PDF, DOCX, or MD file')
        setFile(null)
      }
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('user_id', userId)
      formData.append('prompt', prompt)
      if (file) {
        formData.append('file', file)
      }

      const response = await axios.post('/api/generate', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Content generation failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="view-container">
      <h2 className="view-title">👤 Agent View - Generate Compliant Content</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Your Prompt *</label>
          <textarea
            className="form-textarea"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter your content generation request (e.g., 'Generate a financial disclaimer for investment products')"
            rows="5"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Upload Document (Optional)</label>
          <input
            type="file"
            className="file-input"
            onChange={handleFileChange}
            accept=".pdf,.docx,.md"
          />
          {file && (
            <p style={{ marginTop: '0.5rem', color: '#38a169', fontSize: '0.9rem' }}>
              ✓ Selected: {file.name}
            </p>
          )}
          <p style={{ marginTop: '0.5rem', color: '#718096', fontSize: '0.85rem' }}>
            Supported formats: PDF, DOCX, Markdown
          </p>
        </div>

        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? (
            <>
              <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></div>
              Generating...
            </>
          ) : (
            <>🚀 Generate Compliant Content</>
          )}
        </button>
      </form>

      {error && (
        <div className="alert alert-error" style={{ marginTop: '1.5rem' }}>
          <span>❌</span>
          <div>{error}</div>
        </div>
      )}

      {result && (
        <div style={{ marginTop: '2rem' }}>
          <div className={`alert ${result.is_approved ? 'alert-success' : 'alert-error'}`}>
            <span>{result.is_approved ? '✅' : '❌'}</span>
            <div>
              <strong>Compliance Status: {result.compliance_status.toUpperCase()}</strong>
              <p style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>
                {result.decision_reason}
              </p>
            </div>
          </div>

          <div className="card" style={{ marginTop: '1rem' }}>
            <h3 style={{ marginBottom: '1rem', color: '#2d3748' }}>📄 Generated Content</h3>
            <div style={{ 
              background: '#f7fafc', 
              padding: '1.5rem', 
              borderRadius: '8px',
              whiteSpace: 'pre-wrap',
              lineHeight: '1.6'
            }}>
              {result.generated_content}
            </div>
          </div>

          {result.violations && result.violations.length > 0 && (
            <div className="card" style={{ marginTop: '1rem' }}>
              <h3 style={{ marginBottom: '1rem', color: '#2d3748' }}>
                ⚠️ Rule Violations ({result.total_violations})
              </h3>
              <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                <span className="badge badge-danger">
                  HARD: {result.hard_violations}
                </span>
                <span className="badge badge-warning">
                  SOFT: {result.soft_violations}
                </span>
              </div>
              
              {result.violations.map((violation, index) => (
                <div 
                  key={index} 
                  style={{ 
                    background: violation.severity === 'hard' ? '#fed7d7' : '#feebc8',
                    padding: '1rem',
                    borderRadius: '8px',
                    marginBottom: '0.75rem',
                    borderLeft: `4px solid ${violation.severity === 'hard' ? '#e53e3e' : '#dd6b20'}`
                  }}
                >
                  <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>
                    <span className={`badge ${violation.severity === 'hard' ? 'badge-danger' : 'badge-warning'}`}>
                      {violation.severity.toUpperCase()}
                    </span>
                  </div>
                  <p style={{ marginBottom: '0.5rem' }}>
                    <strong>Rule:</strong> {violation.rule_text}
                  </p>
                  <p style={{ marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                    <strong>Context:</strong> {violation.context}
                  </p>
                  {violation.violated_text && (
                    <p style={{ fontSize: '0.85rem', fontStyle: 'italic', color: '#4a5568' }}>
                      "{violation.violated_text}"
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}

          {result.soft_annotations && (
            <div className="alert alert-warning" style={{ marginTop: '1rem' }}>
              <span>ℹ️</span>
              <div style={{ whiteSpace: 'pre-wrap' }}>{result.soft_annotations}</div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AgentView
