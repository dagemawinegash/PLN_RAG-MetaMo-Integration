import { useState } from 'react'

const formatDate = (value) => {
  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(value))
}

const Sidebar = ({
  chats,
  activeChatId,
  activeView,
  onNewChat,
  onOpenChat,
  onDeleteChat,
  onSelectView,
  newChatDisabled,
}) => {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      className={`sidebar ${collapsed ? 'sidebar-collapsed' : ''}`}
      aria-label="Saved chat history"
    >
      <div className="sidebar-header">
        <div className="sidebar-title">
          <h2>Qwestor</h2>
          <p>Chat history</p>
        </div>
        <button
          className="sidebar-toggle"
          type="button"
          onClick={() => setCollapsed((isCollapsed) => !isCollapsed)}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
          >
            {collapsed ? <path d="M9 18l6-6-6-6" /> : <path d="M15 18l-6-6 6-6" />}
          </svg>
        </button>
      </div>

      <div className="sidebar-actions">
        <button
          type="button"
          onClick={() => {
            onSelectView('home')
            onNewChat()
          }}
          disabled={newChatDisabled}
          className={activeView === 'home' ? 'sidebar-button-active' : ''}
        >
          <span>New chat</span>
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
          >
            <path d="M12 5v14" />
            <path d="M5 12h14" />
          </svg>
        </button>
      </div>

      <div className="history-list">
        {chats.length === 0 ? (
          <p className="history-empty">Saved chats will appear here.</p>
        ) : (
          chats.map((chat) => (
            <div
              className={`history-item ${chat.id === activeChatId ? 'history-item-active' : ''}`}
              key={chat.id}
            >
              <button
                className="history-open"
                type="button"
                onClick={() => onOpenChat(chat.id)}
              >
                <span>{chat.title}</span>
                <small>{formatDate(chat.updatedAt)}</small>
              </button>
              <button
                className="history-delete"
                type="button"
                onClick={() => onDeleteChat(chat.id)}
                aria-label={`Delete ${chat.title}`}
                title="Delete chat"
              >
                <svg
                  aria-hidden="true"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                >
                  <path d="M3 6h18" />
                  <path d="M8 6V4h8v2" />
                  <path d="M19 6l-1 14H6L5 6" />
                  <path d="M10 11v5" />
                  <path d="M14 11v5" />
                </svg>
              </button>
            </div>
          ))
        )}
      </div>

      <div className="sidebar-footer">
        <button
          type="button"
          className={`sidebar-settings ${activeView === 'settings' ? 'sidebar-settings-active' : ''}`}
          onClick={() => onSelectView('settings')}
          aria-label="Open settings"
          title="Settings"
        >
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
          >
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82L4.21 7.2a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33h.01a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51h.01a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v.01a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
          </svg>
          <span>Settings</span>
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
