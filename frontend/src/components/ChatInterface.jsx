import { useState, useRef, useEffect } from 'react'
import { sendQuery } from '../services/api'
import SourcePanel from './SourcePanel'

export default function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [expandedSources, setExpandedSources] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = { role: 'user', content: input.trim() }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)
    setExpandedSources(null)

    try {
      const data = await sendQuery(input.trim())
      const botMsg = {
        role: 'bot',
        content: data.answer,
        sources: data.sources,
      }
      setMessages((prev) => [...prev, botMsg])
    } catch (err) {
      const errMsg = {
        role: 'bot',
        content: `Error: ${err.response?.data?.detail || err.message}`,
      }
      setMessages((prev) => [...prev, errMsg])
    } finally {
      setLoading(false)
    }
  }

  const toggleSources = (index) => {
    setExpandedSources(expandedSources === index ? null : index)
  }

  return (
    <>
      <div className="messages-container">
        {messages.length === 0 && !loading && (
          <div className="welcome-message">
            <h2>RAG Chatbot</h2>
            <p>Upload documents in the sidebar, then ask questions about them.</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i}>
            <div className={`message ${msg.role}`}>
              {msg.content}
            </div>
            {msg.sources && msg.sources.length > 0 && (
              <>
                <button
                  className="source-toggle"
                  onClick={() => toggleSources(i)}
                >
                  {expandedSources === i ? 'Hide sources' : 'View sources'}
                </button>
                {expandedSources === i && (
                  <SourcePanel sources={msg.sources} />
                )}
              </>
            )}
          </div>
        ))}

        {loading && (
          <div className="message loading">Thinking...</div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <form className="input-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your documents..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </>
  )
}
