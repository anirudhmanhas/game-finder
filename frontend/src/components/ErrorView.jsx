import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function ErrorView({ message, onRetry }) {
  return (
    <div className="container" style={{ animation: 'fadeIn 0.5s ease-out' }}>
      <div className="glass" style={{ padding: '3rem', textAlign: 'center', maxWidth: '600px', margin: '0 auto', marginTop: '2rem' }}>
        <AlertCircle size={64} style={{ color: 'var(--accent-color)', marginBottom: '1rem' }} />
        <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Oops! Something went wrong</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          {message || "We encountered an unexpected error while processing your request."}
        </p>
        <button className="btn" onClick={onRetry} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
          <RefreshCw size={20} />
          Try Again
        </button>
      </div>
    </div>
  );
}
