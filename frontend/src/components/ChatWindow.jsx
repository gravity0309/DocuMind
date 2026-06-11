import MessageBubble from './MessageBubble.jsx'

function ChatWindow({ messages, uploaded, messagesEndRef }) {
  if (!uploaded) {
    return (
      <section className="empty-state" aria-label="Getting started">
        <div className="empty-illustration" aria-hidden="true">
          <div className="empty-document">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <div className="empty-search"></div>
        </div>
        <h2>Start chatting with your documents</h2>
        <p>Upload a PDF and ask questions using AI-powered search.</p>
      </section>
    )
  }

  return (
    <section className="messages-area" aria-label="Chat messages">
      {messages.length === 0 ? (
        <div className="empty-conversation">
          <h2>Ask your first question</h2>
          <p>Try asking for a summary, key decisions, action items, or specific details in the PDF.</p>
        </div>
      ) : (
        messages.map((message) => <MessageBubble key={message.id} message={message} />)
      )}
      <div ref={messagesEndRef} />
    </section>
  )
}

export default ChatWindow
