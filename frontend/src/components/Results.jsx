import React, { useState } from 'react';
import GameCard from './GameCard';
import FilterBar from './FilterBar';
import { Gamepad2, SearchX, Wand2 } from 'lucide-react';
import { API_BASE_URL, generateGame as apiGenerateGame } from '../api';

export default function Results({ results, generatedGame, setGeneratedGame, canGenerate, currentPrompt, filters, setFilters }) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateError, setGenerateError] = useState('');

  const handleGenerateClick = async () => {
    setIsGenerating(true);
    setGenerateError('');
    try {
      const response = await apiGenerateGame(currentPrompt);
      if (response.playable) {
        setGeneratedGame(response);
      } else {
        setGenerateError(response.reason_if_not_playable || 'Could not generate game.');
      }
    } catch (e) {
      console.error(e);
      setGenerateError('Failed to generate game. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };
  return (
    <div className="container" style={{ animation: 'fadeIn 0.5s ease-out' }}>
      
      {/* Generated Game Section */}
      {generatedGame && generatedGame.playable && (
        <div className="generated-game-section" style={{ marginBottom: '2rem' }}>
          <h2 className="section-title">
            <Gamepad2 size={28} style={{ color: 'var(--accent-color)' }} />
            Your Generated Game
          </h2>
          <div className="iframe-container">
            <iframe 
              src={`${API_BASE_URL}/games/${generatedGame.game_id}/play`}
              title="Generated Game"
              sandbox="allow-scripts allow-same-origin"
            />
          </div>
        </div>
      )}

      {/* Generate Button Section */}
      {!generatedGame && canGenerate && (
        <div className="glass" style={{ padding: '2rem', marginBottom: '2rem', textAlign: 'center' }}>
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
            <Wand2 size={24} style={{ color: 'var(--accent-color)' }} />
            Want to play this right now?
          </h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            Our AI can generate a lightweight 2D mini-game based on your idea in about 60 seconds!
          </p>
          {isGenerating ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
              <div className="spinner"></div>
              <span style={{ color: 'var(--accent-color)', fontWeight: 500 }}>Generating your mini-game...</span>
            </div>
          ) : (
            <button 
              className="primary-btn" 
              onClick={handleGenerateClick}
              style={{ fontSize: '1.1rem', padding: '0.75rem 2rem' }}
            >
              Generate Mini-Game
            </button>
          )}
          {generateError && (
            <p style={{ color: '#ef4444', marginTop: '1rem' }}>{generateError}</p>
          )}
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
