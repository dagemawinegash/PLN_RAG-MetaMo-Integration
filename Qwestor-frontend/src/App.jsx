import { useEffect, useRef, useState } from 'react'
import ChatWindow from './components/ChatWindow.jsx'
import InputBox from './components/InputBox.jsx'
import Sidebar from './components/Sidebar.jsx'
import PLNTools from './components/PLNTools.jsx'
import {
  ingestTexts,
  queryPln,
  resetPln,
  sendChat,
} from './api/client.js'

const STORAGE_KEY = 'qwestor-chat-history'

const welcomeMessage = {
  role: 'assistant',
  content: 'Hi, I am Qwestor. What do you want to search.',
}

const getSavedChats = () => {
  try {
    const savedChats = localStorage.getItem(STORAGE_KEY)
    return savedChats ? JSON.parse(savedChats) : []
  } catch {
    return []
  }
}

const createChatTitle = (messages) => {
  const firstUserMessage = messages.find((message) => message.role === 'user')

  if (!firstUserMessage) {
    return 'New chat'
  }

  return firstUserMessage.content.length > 42
    ? `${firstUserMessage.content.slice(0, 42)}...`
    : firstUserMessage.content
}

const hasUserMessage = (messages) => {
  return messages.some((message) => message.role === 'user')
}

const App = () => {
  const [messages, setMessages] = useState([welcomeMessage])
  const [savedChats, setSavedChats] = useState(getSavedChats)
  const [activeChatId, setActiveChatId] = useState(null)
  const [activeView, setActiveView] = useState('home')
  const [draftMessage, setDraftMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const [ingestInput, setIngestInput] = useState('')
  const [ingestLoading, setIngestLoading] = useState(false)
  const [ingestResult, setIngestResult] = useState(null)
  const [ingestError, setIngestError] = useState('')

  const [queryInput, setQueryInput] = useState('')
  const [queryLoading, setQueryLoading] = useState(false)
  const [queryResult, setQueryResult] = useState(null)
  const [queryError, setQueryError] = useState('')

  const [resetScope, setResetScope] = useState('all')
  const [resetLoading, setResetLoading] = useState(false)
  const [resetResult, setResetResult] = useState(null)
  const [resetError, setResetError] = useState('')

  const chatEndRef = useRef(null)
  const isNewChat = !hasUserMessage(messages)
  const showCenteredInput = activeView === 'home' && isNewChat && !loading

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(savedChats))
  }, [savedChats])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const saveChatToHistory = (chatMessages, chatId = activeChatId) => {
    if (!hasUserMessage(chatMessages)) {
      return null
    }

    const now = new Date().toISOString()

    if (chatId) {
      setSavedChats((currentChats) =>
        currentChats.map((chat) =>
          chat.id === chatId
            ? {
                ...chat,
                title: createChatTitle(chatMessages),
                messages: chatMessages,
                updatedAt: now,
              }
            : chat,
        ),
      )
      return chatId
    }

    const newChat = {
      id: crypto.randomUUID(),
      title: createChatTitle(chatMessages),
      messages: chatMessages,
      updatedAt: now,
    }

    setSavedChats((currentChats) => [newChat, ...currentChats])
    setActiveChatId(newChat.id)

    return newChat.id
  }

  const sendMessage = async (content) => {
    const trimmedMessage = content.trim()

    if (!trimmedMessage || loading) {
      return
    }

    const userMessages = [...messages, { role: 'user', content: trimmedMessage }]
    const chatId = saveChatToHistory(userMessages)
    const sessionId = chatId || activeChatId || 'default'

    setDraftMessage('')
    setMessages(userMessages)
    setLoading(true)

    try {
      const data = await sendChat({ query: trimmedMessage, session_id: sessionId })
      const assistantMessages = [
        ...userMessages,
        {
          role: 'assistant',
          content: data.answer || 'Something went wrong.',
        },
      ]

      setMessages(assistantMessages)
      saveChatToHistory(assistantMessages, chatId)
    } catch {
      const errorMessages = [
        ...userMessages,
        { role: 'assistant', content: 'Something went wrong.' },
      ]

      setMessages(errorMessages)
      saveChatToHistory(errorMessages, chatId)
    } finally {
      setLoading(false)
    }
  }

  const handleIngestSubmit = async (event) => {
    event.preventDefault()

    if (!ingestInput.trim() || ingestLoading) {
      return
    }

    const texts = ingestInput
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)

    if (texts.length === 0) {
      return
    }

    setIngestLoading(true)
    setIngestError('')
    setIngestResult(null)

    try {
      const data = await ingestTexts(texts)
      setIngestResult(data)
    } catch (error) {
      setIngestError(error.message || 'Failed to ingest.')
    } finally {
      setIngestLoading(false)
    }
  }

  const handleQuerySubmit = async (event) => {
    event.preventDefault()

    if (!queryInput.trim() || queryLoading) {
      return
    }

    setQueryLoading(true)
    setQueryError('')
    setQueryResult(null)

    try {
      const data = await queryPln(queryInput.trim())
      setQueryResult(data)
    } catch (error) {
      setQueryError(error.message || 'Failed to query.')
    } finally {
      setQueryLoading(false)
    }
  }

  const handleResetSubmit = async (event) => {
    event.preventDefault()

    if (resetLoading) {
      return
    }

    setResetLoading(true)
    setResetError('')
    setResetResult(null)

    try {
      const data = await resetPln(resetScope)
      setResetResult(data)
    } catch (error) {
      setResetError(error.message || 'Failed to reset.')
    } finally {
      setResetLoading(false)
    }
  }

  const startNewChat = () => {
    if (loading) {
      return
    }

    setActiveView('home')
    setMessages([welcomeMessage])
    setActiveChatId(null)
    setDraftMessage('')
  }

  const openSavedChat = (chatId) => {
    const chat = savedChats.find((savedChat) => savedChat.id === chatId)

    if (!chat || loading) {
      return
    }

    setActiveView('home')
    setMessages(chat.messages)
    setActiveChatId(chat.id)
    setDraftMessage('')
  }

  const deleteSavedChat = (chatId) => {
    setSavedChats((currentChats) => currentChats.filter((chat) => chat.id !== chatId))

    if (activeChatId === chatId) {
      setMessages([welcomeMessage])
      setActiveChatId(null)
      setDraftMessage('')
    }
  }

  const updateDraftMessage = (value) => {
    setDraftMessage(value)
  }

  return (
    <main className="app-shell">
      <Sidebar
        chats={savedChats}
        activeChatId={activeChatId}
        activeView={activeView}
        onNewChat={startNewChat}
        onOpenChat={openSavedChat}
        onDeleteChat={deleteSavedChat}
        onSelectView={setActiveView}
        newChatDisabled={loading}
      />

      <section
        className={`chat-panel ${showCenteredInput ? 'chat-panel-centered' : ''}`}
        aria-label={activeView === 'settings' ? 'Qwestor settings' : 'Qwestor chatbot'}
      >
        <header className="chat-header">
          <div>
            <h1>{activeView === 'settings' ? 'Settings' : 'Qwestor'}</h1>
            <p>{activeView === 'settings' ? 'PLN tools and controls' : 'AI assistant'}</p>
          </div>
        </header>

        {activeView === 'settings' ? (
          <div className="settings-page">
            <PLNTools
              ingestInput={ingestInput}
              onIngestInputChange={setIngestInput}
              onIngestSubmit={handleIngestSubmit}
              ingestLoading={ingestLoading}
              ingestResult={ingestResult}
              ingestError={ingestError}
              queryInput={queryInput}
              onQueryInputChange={setQueryInput}
              onQuerySubmit={handleQuerySubmit}
              queryLoading={queryLoading}
              queryResult={queryResult}
              queryError={queryError}
              resetScope={resetScope}
              onResetScopeChange={setResetScope}
              onResetSubmit={handleResetSubmit}
              resetLoading={resetLoading}
              resetResult={resetResult}
              resetError={resetError}
            />
          </div>
        ) : (
          <div className="chat-layout">
            <div className="chat-main">
              {showCenteredInput ? (
                <div className="center-composer">
                  <div className="center-composer-inner">
                    <h2>What do you want to search?</h2>
                    <InputBox
                      value={draftMessage}
                      onChange={updateDraftMessage}
                      onSend={sendMessage}
                      disabled={loading}
                    />
                  </div>
                </div>
              ) : (
                <>
                  <ChatWindow messages={messages} loading={loading} chatEndRef={chatEndRef} />
                  <InputBox
                    value={draftMessage}
                    onChange={updateDraftMessage}
                    onSend={sendMessage}
                    disabled={loading}
                  />
                </>
              )}
            </div>
          </div>
        )}
      </section>
    </main>
  )
}

export default App
