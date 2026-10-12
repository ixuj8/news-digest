import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [sections, setSections] = useState([]);
  const [articles, setArticles] = useState([]);
  const [selectedSection, setSelectedSection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 1. Fetch sections on mount
  useEffect(() => {
    fetch('http://localhost:8000/sections')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch sections');
        return res.json();
      })
      .then((data) => {
        setSections(data);
        if (data.length > 0) setSelectedSection(data[0].slug);
      })
      .catch((err) => setError(err.message));
  }, []);

  // 2. Fetch articles when selectedSection changes
  useEffect(() => {
    setLoading(true);
    const url = selectedSection
      ? `http://localhost:8000/articles?section=${selectedSection}`
      : 'http://localhost:8000/articles';

    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch articles');
        return res.json();
      })
      .then((data) => {
        setArticles(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [selectedSection]);

  if (error) return <div style={{ color: 'red', padding: '2rem' }}>Error: {error}</div>;

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>News Aggregator</h1>

      {/* Section Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '2rem', borderBottom: '1px solid #ccc', paddingBottom: '1rem' }}>
        {sections.map((sec) => (
          <button
            key={sec.id}
            onClick={() => setSelectedSection(sec.slug)}
            style={{
              padding: '8px 16px',
              cursor: 'pointer',
              background: selectedSection === sec.slug ? '#007bff' : '#f0f0f0',
              color: selectedSection === sec.slug ? '#fff' : '#333',
              border: 'none',
              borderRadius: '4px'
            }}
          >
            {sec.name}
          </button>
        ))}
      </div>

      {/* Article List & Loading States */}
      {loading ? (
        <p>Loading articles...</p>
      ) : articles.length === 0 ? (
        <p>No articles found for this section.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {articles.map((article) => (
            <li key={article.id} style={{ marginBottom: '1.5rem', borderBottom: '1px solid #eee', paddingBottom: '1rem' }}>
              <a href={article.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '1.2rem', color: '#007bff', textDecoration: 'none' }}>
                {article.title}
              </a>
              <p style={{ color: '#666', margin: '0.5rem 0' }}>{article.snippet}</p>
              <small style={{ color: '#999' }}>Published: {new Date(article.published_at).toLocaleString()}</small>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
