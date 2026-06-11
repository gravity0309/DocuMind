function Sidebar({ uploaded, filename, messageCount, messages, onNewChat }) {
  const lastUserMessage = [...messages].reverse().find((message) => message.type === 'user')

  return (
    <aside className="sidebar" aria-label="Conversation history">
      <div className="brand">
        <div className="brand-mark" aria-hidden="true">
          D
        </div>
        <div>
          <h2>DocuMind</h2>
          <p>Document intelligence</p>
        </div>
      </div>

      <button className="button button-primary new-chat-button" type="button" onClick={onNewChat}>
        New Chat
      </button>

      <section className="sidebar-section" aria-labelledby="history-heading">
        <h3 id="history-heading">History</h3>
        {uploaded ? (
          <button className="history-item active" type="button">
            <span className="history-title">{filename || 'Uploaded PDF'}</span>
            <span className="history-meta">{messageCount} messages</span>
            {lastUserMessage && <span className="history-preview">{lastUserMessage.content}</span>}
          </button>
        ) : (
          <p className="muted-box">Upload a PDF to begin a saved conversation.</p>
        )}
      </section>

      <section className="sidebar-section uploaded-file" aria-labelledby="file-heading">
        <h3 id="file-heading">Uploaded File</h3>
        {uploaded ? (
          <div className="file-card">
            <div className="file-icon" aria-hidden="true">
              PDF
            </div>
            <div>
              <p>{filename}</p>
              <span>Ready for questions</span>
            </div>
          </div>
        ) : (
          <p className="muted-box">No document selected.</p>
        )}
      </section>
    </aside>
  )
}

export default Sidebar
