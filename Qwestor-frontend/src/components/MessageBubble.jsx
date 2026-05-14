const MessageBubble = ({ role, content }) => {
  const isUser = role === 'user'

  return (
    <div className={`message-row ${isUser ? 'message-row-user' : 'message-row-assistant'}`}>
      <div className={`message-bubble ${isUser ? 'message-user' : 'message-assistant'}`}>
        {content}
      </div>
    </div>
  )
}

export default MessageBubble
