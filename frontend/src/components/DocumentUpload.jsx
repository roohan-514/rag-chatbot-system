import { useState, useCallback } from 'react'
import { uploadDocument, listDocuments } from '../services/api'

export default function DocumentUpload({ onDocumentsChange }) {
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [status, setStatus] = useState(null)
  const [docs, setDocs] = useState([])

  const refreshDocs = async () => {
    try {
      const data = await listDocuments()
      setDocs(data)
      if (onDocumentsChange) onDocumentsChange(data)
    } catch {
      // silent
    }
  }

  const handleUpload = useCallback(async (file) => {
    const allowed = ['.pdf', '.txt', '.md']
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
    if (!allowed.includes(ext)) {
      setStatus({ type: 'error', text: `Unsupported file type: ${ext}` })
      return
    }

    setUploading(true)
    setStatus({ type: 'uploading', text: `Uploading ${file.name}...` })

    try {
      const data = await uploadDocument(file)
      setStatus({
        type: 'success',
        text: data.message || `Ingested ${file.name} (${data.chunk_count} chunks)`,
      })
      await refreshDocs()
    } catch (err) {
      setStatus({
        type: 'error',
        text: err.response?.data?.detail || err.message,
      })
    } finally {
      setUploading(false)
    }
  }, [onDocumentsChange])

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragging(true)
  }

  const handleDragLeave = () => setDragging(false)

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0) handleUpload(files[0])
  }

  const handleFileSelect = (e) => {
    const files = e.target.files
    if (files.length > 0) handleUpload(files[0])
    e.target.value = ''
  }

  return (
    <>
      <div
        className={`upload-dropzone ${dragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input').click()}
      >
        <div className="icon">📄</div>
        <p>Drag & drop a document here</p>
        <p>or click to browse</p>
        <p style={{ fontSize: 11, marginTop: 4, color: 'var(--text-secondary)' }}>
          Supports PDF, TXT, MD
        </p>
        <input
          id="file-input"
          type="file"
          accept=".pdf,.txt,.md"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
      </div>

      {status && (
        <div className={`upload-progress ${status.type}`}>
          {status.text}
        </div>
      )}

      <div className="documents-list">
        <h4>Ingested Documents</h4>
        {docs.length === 0 ? (
          <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
            No documents ingested yet.
          </p>
        ) : (
          <ul>
            {docs.map((doc) => (
              <li key={doc.id}>
                {doc.filename} ({doc.chunk_count} chunks)
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  )
}
