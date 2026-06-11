function MessageBubble({ message }) {
  const isAi = message.type === 'ai'

  return (
    <article className={`message-row ${isAi ? 'message-ai' : 'message-user'}`}>
      {isAi && (
        <div className="message-avatar" aria-hidden="true">
          AI
        </div>
      )}

      <div className="message-stack">
        <div className={`message-bubble ${message.error ? 'message-error' : ''}`}>
          {message.loading ? (
            <div className="typing-indicator" role="status" aria-label="DocuMind is thinking">
              <span></span>
              <span></span>
              <span></span>
            </div>
          ) : (
            <>
              <p>{message.content}</p>
              {isAi && (
                <div className="source-block">
                  <span>Source</span>
                  <strong>Uploaded PDF</strong>
                </div>
              )}
            </>
          )}
        </div>
        <time className="message-time">{message.timestamp}</time>
      </div>
    </article>
  )
}

export default MessageBubble
