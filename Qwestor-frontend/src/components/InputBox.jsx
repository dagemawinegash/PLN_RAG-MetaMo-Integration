const InputBox = ({ value, onChange, onSend, disabled }) => {
  const handleSubmit = (event) => {
    event.preventDefault()

    if (!value.trim() || disabled) {
      return
    }

    onSend(value)
  }

  return (
    <form className="input-form" onSubmit={handleSubmit}>
      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Ask Qwestor anything..."
        disabled={disabled}
        aria-label="Message"
      />
      <button type="submit" disabled={disabled || !value.trim()}>
        Send
      </button>
    </form>
  )
}

export default InputBox
