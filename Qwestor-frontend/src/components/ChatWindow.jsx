import MessageBubble from './MessageBubble.jsx'

const ChatWindow = ({ messages, loading, chatEndRef }) => {
  return (
    <div className="chat-window">
      {messages.length === 0 ? (
        <div className="empty-state">Start a new chat.</div>
      ) : (
        messages.map((message, index) => (
          <MessageBubble
            key={`${message.role}-${index}`}
            role={message.role}
            content={message.content}
          />
        ))
      )}

      {loading && <MessageBubble role="assistant" content="Thinking..." />}
      <div ref={chatEndRef} />
    </div>
  )
}

export default ChatWindow
