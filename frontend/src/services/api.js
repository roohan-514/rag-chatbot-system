import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function healthCheck() {
  const res = await api.get('/health')
  return res.data
}

export async function uploadDocument(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await api.post('/ingest', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function sendQuery(query, k = 4) {
  const res = await api.post('/query', { query, k })
  return res.data
}

export async function listDocuments() {
  const res = await api.get('/documents')
  return res.data
}
