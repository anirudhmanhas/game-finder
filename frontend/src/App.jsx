import React, { useState, useEffect } from 'react';
import Home from './components/Home';
import Results from './components/Results';
import Clarify from './components/Clarify';
import ErrorView from './components/ErrorView';
import { searchGames } from './api';
import { Gamepad2 } from 'lucide-react';

export default function App() {
  const [viewState, setViewState] = useState('home'); // 'home', 'loading', 'results', 'clarify'
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [filters, setFilters] = useState({ genre: [], multiplayer: false });
  
  const [results, setResults] = useState([]);
  const [generatedGame, setGeneratedGame] = useState(null);
  const [canGenerate, setCanGenerate] = useState(false);
  const [clarifyData, setClarifyData] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  // Trigger search whenever filters change, if we're on the results page
  useEffect(() => {
    if (viewState === 'results' && currentPrompt) {
      handleSearch(currentPrompt, filters, true);
    }
  }, [filters]);

  const handleSearch = async (prompt, activeFilters = {}, isFilterUpdate = false) => {
    setCurrentPrompt(prompt);
    if (!isFilterUpdate) {
      setViewState('loading');
      setGeneratedGame(null);
      setFilters(activeFilters);
    }

    try {
      // Single unified call
      const response = await searchGames(prompt, activeFilters);
      
      if (response.clarification_needed) {
        setClarifyData(response.suggested_question);
        setViewState('clarify');
        return;
      }
      
      setResults(response.recommendations || []);
      setCanGenerate(response.can_generate || false);
      
      // Update generated game only on fresh searches
      if (!isFilterUpdate && response.generated_game) {
        if (response.generated_game.playable) {
            setGeneratedGame(response.generated_game);
        }
      }

      setViewState('results');
    } catch (err) {
      console.error("Search failed:", err);
      // Catching rate limit or other network errors
      if (err.message && err.message.includes('429')) {
          setErrorMessage("You are searching too fast. Please wait a moment and try again.");
      } else {
          setErrorMessage("Something went wrong processing your request. Please try again later.");
      }
      setViewState('error');
    }
  };

  const handleClarification = (answer) => {
    const combinedPrompt = `${currentPrompt}. Clarification: ${answer}`;
    handleSearch(combinedPrompt, filters, false);
  };

  const resetHome = () => {
    setViewState('home');
    setCurrentPrompt('');
    setFilters({ genre: [], multiplayer: false });
    setResults([]);
    setGeneratedGame(null);
  };

  return (
    <>
      <header className="app-header" onClick={resetHome}>
        <div className="app-logo">
          <Gamepad2 size={24} color="var(--accent-color)" />
          PlayWeave
        </div>
      </header>

      {viewState === 'home' && (
        <Home onSearch={(p) => handleSearch(p, { genre: [], multiplayer: false })} />
      )}

      {viewState === 'loading' && (
        <div className="loading-container">
          <div className="spinner"></div>
          <p className="loading-text" style={{ color: 'var(--text-secondary)', fontSize: '1.2rem', fontWeight: 500, marginTop: '1rem', animation: 'pulse 1.5s infinite' }}>
            Analyzing request and weaving magic...
          </p>
        </div>
      )}

      {viewState === 'clarify' && (
        <Clarify 
          suggestedQuestion={clarifyData} 
          onClarify={handleClarification} 
        />
      )}

      {viewState === 'error' && (
        <ErrorView 
          message={errorMessage} 
          onRetry={resetHome} 
        />
      )}

      {viewState === 'results' && (
        <Results 
          results={results} 
          generatedGame={generatedGame} 
          setGeneratedGame={setGeneratedGame}
          canGenerate={canGenerate}
          currentPrompt={currentPrompt}
          filters={filters}
          setFilters={setFilters}
        />
      )}

      <footer style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)', marginTop: 'auto' }}>
        Made by Boiler_Plate_Dine
      </footer>
    </>
  );
}
