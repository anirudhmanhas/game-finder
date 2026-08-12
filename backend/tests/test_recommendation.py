import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models import Game
from schemas import StructuredQuery
from services.recommendation import calculate_score, get_recommendations

client = TestClient(app)

def test_calculate_score():
    game = Game(
        id=uuid4(),
        genres=["Action", "RPG"],
        tags=["Open World"],
        platforms=["PC"]
    )
    query = StructuredQuery(
        genres=["RPG"],
        sub_genres=[],
        mechanics=["Open World"],
        platform_preference="PC",
        intent_summary="test"
    )
    user_history = ["Action"]
    
    score = calculate_score(game, query, user_history)
    
    # 0.4 (base) + 0.2 (genre RPG) + 0.1 (mechanic) + 0.1 (platform) + 0.05 (user history Action) = 0.85
    assert abs(score - 0.85) < 0.01

@patch('services.recommendation.interpret_prompt')
@patch('services.recommendation.GameRepository')
def test_get_recommendations_fallback(MockRepo, mock_interpret):
    # Setup mock query
    mock_query = StructuredQuery(
        genres=["Sci-Fi"],
        intent_summary="test intent",
        embedding=[0.1, 0.2]
    )
    mock_interpret.return_value = mock_query
    
    # Setup mock repo that returns poor results
    mock_repo_instance = MagicMock()
    MockRepo.return_value = mock_repo_instance
    
    poor_game = Game(id=uuid4(), title="Poor Match", genres=["Puzzle"], tags=[], platforms=[], created_at=datetime.utcnow())
    mock_repo_instance.search_similar_games.return_value = [poor_game]
    
    mock_db = MagicMock()
    result = get_recommendations("dummy prompt", None, mock_db)
    
    assert result["clarification_needed"] is False
    assert len(result["results"]) > 0
    
    # External result should be injected and ranked highest because of low score of internal
    top_result = result["results"][0]
    assert top_result["is_external"] is True
    assert top_result["source"] == "mock_igdb"

@patch('main.get_recommendations')
def test_recommendation_endpoint(mock_get_recs):
    mock_get_recs.return_value = {
        "clarification_needed": False,
        "results": [{"title": "Test Game", "match_score": 0.9}]
    }
    
    response = client.post("/recommendations", json={"prompt": "A test game"})
    
    assert response.status_code == 200
    assert response.json()["results"][0]["title"] == "Test Game"
