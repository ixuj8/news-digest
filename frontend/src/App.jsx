import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [sections, setSections] = useState([]);
  const [articles, setArticles] = useState([]);
  const [selectedSection, setSelectedSection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('jwt_token') || null);

  // New state for Settings view & user preferences
  const [showSettings, setShowSettings] = useState(false);
  const [userSections, setUserSections] = useState([]); // Array of section IDs
  const [customTopics, setCustomTopics] = useState([]); // Array of strings
  const [newTopicInput, setNewTopicInput] = useState('');

  // Capture token from URL query params after GitHub redirect callback
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    if (urlToken) {
      localStorage.setItem('jwt_token', urlToken);
      setToken(urlToken);
      // Clean up URL parameters
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  // Fetch sections on mount
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

  // Fetch user settings when token changes or settings page opens
  useEffect(() => {
    if (token) {
      fetch('http://localhost:8000/user/settings', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then((res) => res.ok ? res.json() : null)
        .then((data) => {
          if (data) {
            setUserSections(data.sections || []);
            setUserTopics(data.topics || []);
          }
        })
        .catch((err) => console.error("Failed to load settings", err));
    }
  }, [token]);

  // Fetch articles when selectedSection changes
  useEffect(() => {
    if (showSettings) return; // Don't fetch articles if looking at settings
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
  }, [selectedSection, showSettings]);

  const handleLogin = () => {
    window.location.href = 'http://localhost:8000/auth/github/login';
  };

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    setToken(null);
    setShowSettings(false);
  };

  // Save settings handler (PUT request)
  const handleSaveSettings = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/user/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ sections: userSections, topics: customTopics })
      });

      if (!res.ok) throw new Error('Failed to save settings');
      alert('Settings saved successfully!');
      setShowSettings(false);
    } catch (err) {
      alert(err.message);
    }
  };

  const handleAddTopic = () => {
    if (newTopicInput.trim() && !customTopics.includes(newTopicInput.trim())) {
      setCustomTopics([...customTopics, newTopicInput.trim()]);
      setNewTopicInput('');
    }
  };

  const handleRemoveTopic = (topicToRemove) => {
    setCustomTopics(customTopics.filter(t => t !== topicToRemove));
  };

  const toggleSectionSelection = (sectionId) => {
    if (userSections.includes(sectionId)) {
      setUserSections(userSections.filter(id => id !== sectionId));
    } else {
      setUserSections([...userSections, sectionId]);
    }
  };

  {/* Determine which sections to display in the navigation tabs */}
  const displayedSections = token && userSections.length > 0
    ? sections.filter((sec) => userSections.includes(sec.id))
    : sections;

  if (error) return <div style={{ color: 'red', padding: '2rem' }}>Error: {error}</div>;

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem', fontFamily: 'sans-serif' }}>

      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 style={{ margin: 0, cursor: 'pointer' }} onClick={() => setShowSettings(false)}>News Digest</h1>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {token ? (
            <>
              <button
                onClick={() => setShowSettings(!showSettings)}
                style={{ padding: '8px 12px', cursor: 'pointer', background: '#e9ecef', border: '1px solid #ced4da', borderRadius: '4px' }}
              >
                {showSettings ? 'Back to News' : '⚙️ Settings'}
              </button>
              <button onClick={handleLogout} style={{ padding: '8px 12px', cursor: 'pointer' }}>
                Logout
              </button>
            </>
          ) : (
            <button onClick={handleLogin} style={{ padding: '8px 12px', cursor: 'pointer', background: '#24292e', color: '#fff', border: 'none', borderRadius: '4px' }}>
              Login with GitHub
            </button>
          )}
        </div>
      </header>

      {/* Conditional View: Settings Page vs. News Feed */}
      {showSettings ? (
        <div style={{ background: '#f8f9fa', padding: '2rem', borderRadius: '8px', border: '1px solid #dee2e6' }}>
          <h2>Customize Your Preferences</h2>
          <form onSubmit={handleSaveSettings}>

            {/* Sections Toggles */}
            <h3 style={{ marginTop: '1.5rem' }}>Preferred Sections</h3>
            <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
              {sections.map((sec) => (
                <label key={sec.id} style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={userSections.includes(sec.id)}
                    onChange={() => toggleSectionSelection(sec.id)}
                  />
                  {sec.name}
                </label>
              ))}
            </div>

            {/* Custom Free-text Topics */}
            <h3>Custom Topics</h3>
            <div style={{ display: 'flex', gap: '10px', marginBottom: '1rem' }}>
              <input
                type="text"
                placeholder="e.g., Grammys, AI, Taylor Swift"
                value={newTopicInput}
                onChange={(e) => setNewTopicInput(e.target.value)}
                style={{ padding: '8px', flex: 1, borderRadius: '4px', border: '1px solid #ccc' }}
              />
              <button type="button" onClick={handleAddTopic} style={{ padding: '8px 16px', cursor: 'pointer' }}>
                Add Topic
              </button>
            </div>

            {/* Topic Chips */}
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '2rem' }}>
              {customTopics.map((topic, index) => (
                <span key={index} style={{ background: '#007bff', color: '#fff', padding: '5px 10px', borderRadius: '15px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem' }}>
                  {topic}
                  <button type="button" onClick={() => handleRemoveTopic(topic)} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', fontWeight: 'bold' }}>×</button>
                </span>
              ))}
            </div>

            <button type="submit" style={{ padding: '10px 20px', background: '#28a745', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '1rem' }}>
              Save Settings
            </button>
          </form>
        </div>
      ) : (
        <>
          {/* Section Tabs (Filtered by User Preferences) */}
          <div style={{ display: 'flex', gap: '10px', marginBottom: '2rem', borderBottom: '1px solid #ccc', paddingBottom: '1rem', overflowX: 'auto' }}>
            {displayedSections.map((sec) => (
              <button
                key={sec.id}
                onClick={() => setSelectedSection(sec.slug)}
                style={{
                  padding: '8px 16px',
                  cursor: 'pointer',
                  background: selectedSection === sec.slug ? '#007bff' : '#f0f0f0',
                  color: selectedSection === sec.slug ? '#fff' : '#333',
                  border: 'none',
                  borderRadius: '4px',
                  whiteSpace: 'nowrap'
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
        </>
      )}
    </div>
  );
}

export default App;
