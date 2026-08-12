import React, { useState } from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';

export default function Home({ onSearch }) {
  const [query, setQuery] = useState('');

  const examples = [
    "A simple 2D bouncing ball game",
    "A fast-paced neon arcade shooter",
    "A cozy farming simulator",
    "A multiplayer puzzle game"
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  return (
    <div className="home-container">
      <h1 className="hero-title">
        PlayWeave
      </h1>
      <p className="hero-subtitle">
        Describe the game you want to play, and our AI will find the perfect match—or generate it instantly.
      </p>

      <form className="search-box" onSubmit={handleSubmit}>
        <div className="input-group">
          <input
            type="text"
            className="input"
            placeholder="e.g. A fast-paced neon arcade shooter..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className="btn input-btn">
            <ArrowRight size={20} />
          </button>
        </div>
      </form>

      <div className="chips-container">
        {examples.map((ex, i) => (
          <div 
            key={i} 
            className="chip"
            onClick={() => {
              setQuery(ex);
              onSearch(ex);
            }}
          >
            <Sparkles size={14} style={{ display: 'inline', marginRight: '4px' }} />
            {ex}
          </div>
        ))}
      </div>
    </div>
  );
}
