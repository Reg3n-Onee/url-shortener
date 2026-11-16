import { useState } from "react";

function App() {
  const [url, setUrl] = useState("");
  const [shortUrl, setShortUrl] = useState("");
  const [code, setCode] = useState("");
  const [stats, setStats] = useState(null);

  const handleShorten = async () => {
    const res = await fetch("/api/shorten", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = await res.json();
    setShortUrl(window.location.origin + data.short_url);
    setCode(data.code);
  };

  const handleStats = async () => {
    const res = await fetch(`/api/stats/${code}`);
    setStats(await res.json());
  };

  return (
    <div style={{ padding: 40, fontFamily: "sans-serif" }}>
      <h1>URL Shortener</h1>
      <input
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://example.com"
        style={{ width: 300 }}
      />
      <button onClick={handleShorten}>Shorten</button>

      {shortUrl && (
        <div style={{ marginTop: 20 }}>
          <p>
            Short link:{" "}
            <a href={shortUrl} target="_blank" rel="noreferrer">
              {shortUrl}
            </a>
          </p>
          <button onClick={handleStats}>Refresh stats</button>
          {stats && <p>Total clicks: {stats.total_clicks}</p>}
        </div>
      )}
    </div>
  );
}

export default App;