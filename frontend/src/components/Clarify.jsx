import React, { useState } from 'react';
import { HelpCircle, ArrowRight } from 'lucide-react';

export default function Clarify({ suggestedQuestion, onClarify }) {
  const [answer, setAnswer] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (answer.trim()) {
      onClarify(answer);
    }
  };

  return (
    <div className="clarify-container glass" style={{ animation: 'slideUp 0.4s ease-out' }}>
      <HelpCircle size={48} className="clarify-icon" />
      <h2 className="clarify-title">Can you be a bit more specific?</h2>
      <p className="clarify-question">{suggestedQuestion}</p>
      
      <form onSubmit={handleSubmit} className="input-group" style={{ marginTop: '1.5rem' }}>
        <input
          type="text"
          className="input"
          placeholder="Type your answer here..."
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          autoFocus
        />
        <button type="submit" className="btn input-btn">
          <ArrowRight size={20} />
        </button>
      </form>
    </div>
  );
}
