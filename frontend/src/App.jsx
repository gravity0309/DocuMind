import { useEffect, useRef, useState } from 'react'
import axios from 'axios'
import Sidebar from './components/Sidebar.jsx'
import UploadSection from './components/UploadSection.jsx'
import ChatWindow from './components/ChatWindow.jsx'
import ChatInput from './components/ChatInput.jsx'
import './App.css'

const API_URL = 'https://documind-production-8c7a.up.railway.app'
const STORAGE_KEYS = {
  messages: 'documind_messages',
  uploaded: 'documind_uploaded',
  filename: 'documind_filename',
  sessionId: 'documind_session_id',
}

const getTimestamp = () => new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })

const normalizeMessages = (savedMessages) => {
  if (!Array.isArray(savedMessages)) {
    return []
  }

  return savedMessages
    .filter((message) => message?.type && message?.content)
    .map((message, index) => ({
      id: Number(message.id || Date.now() + index),
      type: message.type,
      content: message.content,
      timestamp: String(message.timestamp || getTimestamp()),
      error: Boolean(message.error),
    }))
}

function App() {
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploaded, setUploaded] = useState(false)
  const [sessionId, setSessionId] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploadedFilename, setUploadedFilename] = useState('')
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [isDragging, setIsDragging] = useState(false)

  const fileInputRef = useRef(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    const savedMessages = localStorage.getItem(STORAGE_KEYS.messages)
    const savedUploaded = localStorage.getItem(STORAGE_KEYS.uploaded)
    const savedFilename = localStorage.getItem(STORAGE_KEYS.filename)
    const savedSessionId = localStorage.getItem(STORAGE_KEYS.sessionId)

    if (savedMessages) {
      try {
        setMessages(normalizeMessages(JSON.parse(savedMessages)))
      } catch {
        localStorage.removeItem(STORAGE_KEYS.messages)
      }
    }

    if (savedUploaded === 'true') {
      setUploaded(true)
    }

    if (savedFilename) {
      setUploadedFilename(savedFilename)
    }

    if (savedSessionId) {
      setSessionId(savedSessionId)
    }
  }, [])

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.messages, JSON.stringify(messages))
  }, [messages])

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.uploaded, String(uploaded))
  }, [uploaded])

  useEffect(() => {
    if (uploadedFilename) {
      localStorage.setItem(STORAGE_KEYS.filename, uploadedFilename)
    } else {
      localStorage.removeItem(STORAGE_KEYS.filename)
    }
  }, [uploadedFilename])

  useEffect(() => {
    if (sessionId) {
      localStorage.setItem(STORAGE_KEYS.sessionId, sessionId)
    } else {
      localStorage.removeItem(STORAGE_KEYS.sessionId)
    }
  }, [sessionId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const isPdfFile = (file) => {
    return file && (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf'))
  }

  const getFriendlyError = (fallbackMessage, caughtError) => {
    if (!caughtError.response) {
      return 'Unable to reach the DocuMind server. Please make sure the backend is running and try again.'
    }

    return caughtError.response.data?.detail || caughtError.response.data?.message || fallbackMessage
  }

  const resetConversation = () => {
    Object.values(STORAGE_KEYS).forEach((key) => localStorage.removeItem(key))
    setMessages([])
    setQuestion('')
    setLoading(false)
    setUploaded(false)
    setSessionId('')
    setSelectedFile(null)
    setUploadedFilename('')
    setUploading(false)
    setError('')
    setIsDragging(false)
  }

  const uploadPdf = async (file) => {
    const formData = new FormData()
    formData.append('file', file)

    setUploading(true)
    setUploaded(false)
    setSessionId('')
    setMessages([])
    setQuestion('')
    setError('')

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setSessionId(response.data.session_id)
      setUploadedFilename(response.data.filename || file.name)
      setUploaded(true)
    } catch (caughtError) {
      setUploaded(false)
      setUploadedFilename('')
      setError(getFriendlyError('We could not process this PDF. Please try another file.', caughtError))
    } finally {
      setUploading(false)
    }
  }

  const handleFile = (file) => {
    if (!file) {
      return
    }

    if (!isPdfFile(file)) {
      setSelectedFile(null)
      setUploaded(false)
      setSessionId('')
      setMessages([])
      setUploadedFilename('')
      setError('Please choose a PDF file. DocuMind can only process .pdf documents.')
      return
    }

    setSelectedFile(file)
    setUploadedFilename(file.name)
    uploadPdf(file)
  }

  const handleFileChange = (event) => {
    handleFile(event.target.files?.[0])
    event.target.value = ''
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragging(false)
    handleFile(event.dataTransfer.files?.[0])
  }

  const handleDragOver = (event) => {
    event.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (event) => {
    if (!event.currentTarget.contains(event.relatedTarget)) {
      setIsDragging(false)
    }
  }

  const handleSendQuestion = async (event) => {
    event.preventDefault()

    const trimmedQuestion = question.trim()
    if (!trimmedQuestion || loading || !sessionId) {
      return
    }

    const userMessageId = Date.now()
    const aiMessageId = userMessageId + 1

    setQuestion('')
    setLoading(true)
    setError('')
    setMessages((currentMessages) => [
      ...currentMessages,
      {
        id: userMessageId,
        type: 'user',
        content: trimmedQuestion,
        timestamp: getTimestamp(),
      },
      {
        id: aiMessageId,
        type: 'ai',
        content: 'Thinking...',
        timestamp: getTimestamp(),
        loading: true,
      },
    ])

    try {
      const response = await axios.post(`${API_URL}/ask`, {
        session_id: sessionId,
        question: trimmedQuestion,
      })

      setMessages((currentMessages) =>
        currentMessages.map((message) =>
          message.id === aiMessageId
            ? {
                id: aiMessageId,
                type: 'ai',
                content: response.data?.answer || 'DocuMind did not return an answer for that question.',
                timestamp: getTimestamp(),
              }
            : message,
        ),
      )
    } catch {
      setMessages((currentMessages) =>
        currentMessages.map((message) =>
          message.id === aiMessageId
            ? {
                id: aiMessageId,
                type: 'ai',
                content: 'Sorry, something went wrong.',
                timestamp: getTimestamp(),
                error: true,
              }
            : message,
        ),
      )
    } finally {
      setLoading(false)
    }
  }

  const displayFilename = uploadedFilename || selectedFile?.name || ''

  return (
    <main className="app-shell">
      <Sidebar
        uploaded={uploaded}
        filename={displayFilename}
        messageCount={messages.length}
        messages={messages}
        onNewChat={resetConversation}
      />

      <section className="workspace" aria-labelledby="app-title">
        <header className="topbar">
          <div>
            <h1 id="app-title">DocuMind</h1>
            <p>Chat with your documents</p>
          </div>

          <div className="topbar-actions">
            <div className={`status-pill ${uploaded ? 'status-ready' : 'status-idle'}`}>
              <span aria-hidden="true"></span>
              {uploaded ? 'PDF Ready' : 'No PDF'}
            </div>
            <button
              className="button button-secondary"
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading || loading}
            >
              Upload PDF
            </button>
          </div>
        </header>

        <UploadSection
          fileInputRef={fileInputRef}
          uploaded={uploaded}
          uploading={uploading}
          filename={displayFilename}
          isDragging={isDragging}
          error={error}
          onFileChange={handleFileChange}
          onChooseFile={() => fileInputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        />

        <div className="chat-shell">
          <ChatWindow messages={messages} uploaded={uploaded} messagesEndRef={messagesEndRef} />
          <ChatInput
            question={question}
            loading={loading}
            uploaded={uploaded}
            onQuestionChange={setQuestion}
            onSubmit={handleSendQuestion}
          />
        </div>
      </section>
    </main>
  )
}

export default App
