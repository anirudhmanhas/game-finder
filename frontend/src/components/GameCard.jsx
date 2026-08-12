import React, { useState } from 'react';
import { Heart } from 'lucide-react';
import { likeGame } from '../api';

export default function GameCard({ game }) {
  const [liked, setLiked] = useState(false);

  const handleLike = async () => {
    if (liked) return;
    try {
      await likeGame(game.id);
      setLiked(true);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="game-card glass">
      <div className="game-card-content">
        <div className="game-card-header">
          <h3 className="game-title">{game.title}</h3>
          {game.is_external && (
            <span className="game-source-badge">External API</span>
          )}
        </div>
        
        <p className="game-reason">{game.match_reason}</p>
        
        <div className="game-tags">
          {game.genres.slice(0, 2).map((g, i) => (
            <span key={i} className="game-tag">{g}</span>
          ))}
          {game.platforms.slice(0, 1).map((p, i) => (
            <span key={`p-${i}`} className="game-tag">{p}</span>
          ))}
        </div>
        
        <div className="game-card-actions">
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Score: {Math.round(game.match_score * 100)}%
          </span>
          <button 
            className={`like-btn ${liked ? 'liked' : ''}`} 
            onClick={handleLike}
            title="Like this game to improve recommendations"
          >
            <Heart size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
