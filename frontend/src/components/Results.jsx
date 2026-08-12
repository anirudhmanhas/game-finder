import React from 'react';
import GameCard from './GameCard';
import FilterBar from './FilterBar';
import { Gamepad2, SearchX } from 'lucide-react';

export default function Results({ results, generatedGame, filters, setFilters }) {
  return (
    <div className="container" style={{ animation: 'fadeIn 0.5s ease-out' }}>
      
      {/* Generated Game Section */}
      {generatedGame && generatedGame.playable && (
        <div className="generated-game-section">
          <h2 className="section-title">
            <Gamepad2 size={28} style={{ color: 'var(--accent-color)' }} />
            Your Generated Game
          </h2>
          <div className="iframe-container">
            <iframe 
              src={`http://localhost:8001/games/${generatedGame.game_id}/play`}
              title="Generated Game"
              sandbox="allow-scripts allow-same-origin"
            />
          </div>
        </div>
      )}

      {/* Recommendations Layout */}
      <h2 className="section-title">Recommended for You</h2>
      <div className="results-layout">
        
        {/* Sidebar Filters */}
        <FilterBar filters={filters} setFilters={setFilters} />
        
        {/* Games Grid */}
        <div className="games-grid">
          {results.length > 0 ? (
            results.map((game, idx) => (
              <GameCard key={game.id || idx} game={game} />
            ))
          ) : (
            <div className="glass empty-state" style={{ padding: '4rem 2rem', textAlign: 'center', gridColumn: '1 / -1', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
              <SearchX size={48} style={{ color: 'var(--text-secondary)' }} />
              <h3 style={{ fontSize: '1.25rem' }}>No games found</h3>
              <p style={{ color: 'var(--text-secondary)', maxWidth: '400px' }}>
                We couldn't find any recommendations matching your current filters. Try adjusting them or searching for something else.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
