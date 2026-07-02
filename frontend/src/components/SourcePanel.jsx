export default function SourcePanel({ sources }) {
  if (!sources || sources.length === 0) return null

  return (
    <div className="sources-panel">
      <h4>Sources</h4>
      {sources.map((source, i) => (
        <div key={i} className="source-item">
          <div className="filename">
            {source.filename}
            {source.page != null && ` (p. ${source.page})`}
          </div>
          <div className="score">
            Relevance: {(source.score * 100).toFixed(1)}%
          </div>
          <div style={{ fontSize: 12, marginTop: 2, color: 'var(--text-secondary)' }}>
            {source.content}
          </div>
        </div>
      ))}
    </div>
  )
}
