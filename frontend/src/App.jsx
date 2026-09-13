import { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    fetch("/api/health/")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Health check failed: ${response.status}`);
        }

        return response.json();
      })
      .then((data) => {
        setMessage(data.message);
      })
      .catch(() => {
        setMessage("Backend connection failed");
      });
  }, []);

  return (
    <div>
      <h1>Developer Documentation Assistant</h1>
      <p>{message}</p>
    </div>
  );
}

export default App;