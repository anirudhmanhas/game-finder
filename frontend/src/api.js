export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function searchGames(prompt, filters = {}) {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt,
      filters
    }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to search games');
  }
  
  return response.json();
}

export async function likeGame(gameId) {
  // Using a mock user_id for now
  const userId = "mock-user-123";
  const response = await fetch(`${API_BASE_URL}/games/${gameId}/like?user_id=${userId}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error('Failed to like game');
  }
  
  return response.json();
}
