import React from 'react';

export default function FilterBar({ filters, setFilters }) {
  const genres = ['Action', 'RPG', 'Puzzle', 'Strategy', 'Shooter', 'Platformer', 'Simulation'];

  const toggleGenre = (genre) => {
    setFilters(prev => {
      const current = prev.genre || [];
      const updated = current.includes(genre) 
        ? current.filter(g => g !== genre)
        : [...current, genre];
      
      return { ...prev, genre: updated };
    });
  };

  const toggleMultiplayer = () => {
    setFilters(prev => ({
      ...prev,
      multiplayer: !prev.multiplayer
    }));
  };

  return (
    <div className="sidebar glass" style={{ padding: '1.5rem', height: 'fit-content' }}>
      <h3 className="section-title" style={{ fontSize: '1.1rem' }}>Refine Results</h3>
      
      <div className="filter-group">
        <span className="filter-title">Multiplayer</span>
        <label className="filter-label">
          <input 
            type="checkbox" 
            checked={filters.multiplayer || false}
            onChange={toggleMultiplayer}
          />
          Supports Multiplayer
        </label>
      </div>

      <div className="filter-group" style={{ marginTop: '1rem' }}>
        <span className="filter-title">Genres</span>
        {genres.map(genre => (
          <label key={genre} className="filter-label">
            <input 
              type="checkbox" 
              checked={(filters.genre || []).includes(genre)}
              onChange={() => toggleGenre(genre)}
            />
            {genre}
          </label>
        ))}
      </div>
    </div>
  );
}
