
function ChatInput({ question, setQuestion, handleSubmit, loading }) {
  return (
    <form onSubmit={handleSubmit} className="chat-input-form">
      <div className="chat-composer">
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask anything about React, JavaScript, or documentation..."
          rows={1}
          disabled={loading}
        />

        <button
            type="submit"
            disabled={loading || !question.trim()}
            aria-label="Send message"
          >
            {loading ? "..." : "↑"}
          </button>
      </div>
    </form>
  );
}

export default ChatInput;
