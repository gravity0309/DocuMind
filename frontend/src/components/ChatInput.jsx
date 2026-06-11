function ChatInput({ question, loading, uploaded, onQuestionChange, onSubmit }) {
  return (
    <form className="chat-input" onSubmit={onSubmit}>
      <label className="visually-hidden" htmlFor="chat-question">
        Ask a question about your PDF
      </label>
      <input
        id="chat-question"
        type="text"
        value={question}
        onChange={(event) => onQuestionChange(event.target.value)}
        placeholder={uploaded ? 'Ask anything about this PDF...' : 'Upload a PDF to start chatting'}
        disabled={!uploaded || loading}
      />
      <button className="button button-primary send-button" type="submit" disabled={!uploaded || loading || !question.trim()}>
        Send
      </button>
    </form>
  )
}

export default ChatInput
