
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!question.trim() || loading) {
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setCitations([]);

    try {
      const response = await fetch("/api/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Something went wrong.");
      }

      setAnswer(data.answer || "No answer received.");
      setCitations(data.citations || []);
    } catch (err) {
      setError(err.message || "Failed to connect to the backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Developer Documentation Assistant</h1>

      <form onSubmit={handleSubmit}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask a React documentation question..."
          rows={4}
          disabled={loading}
        />

        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? "Generating..." : "Ask"}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}

      {loading && <p>Searching documentation and generating answer...</p>}

      {answer && (
        <div>
          <h2>Answer</h2>

          <ReactMarkdown>{answer}</ReactMarkdown>

          {citations.length > 0 && (
            <div>
              <h3>Documentation Sources</h3>

              <ul>
                {citations.map((citation, index) => (
                  <li key={`${citation.url}-${index}`}>
                    <a
                      href={citation.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {citation.title}
                    </a>
                    {citation.section && <span> — {citation.section}</span>}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
