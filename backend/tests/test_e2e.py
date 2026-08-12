import pytest
from httpx import AsyncClient
from main import app
from schemas import StructuredQuery
import uuid

@pytest.fixture
def mock_gemini(mocker):
    # Mock interpret_prompt
    mock_interpret = mocker.patch("main.interpret_prompt")
    mock_interpret.return_value = StructuredQuery(
        genres=["Arcade"],
        sub_genres=[],
        mechanics=["bouncing", "2D"],
        platform_preference=None,
        multiplayer_support=False,
        tone="fast",
        intent_summary="A simple bouncing ball game",
        needs_clarification=False,
        embedding=[0.1] * 768
    )
    
    # Mock generation pipeline
    mock_generate = mocker.patch("main.generate_game_pipeline")
    mock_generate.return_value = {
        "playable": True,
        "html_content": "<html><body>Mock Game</body></html>",
        "reason": "Generated successfully"
    }
    
    # Mock recommendation fetch
    mock_recs = mocker.patch("main.get_recommendations")
    mock_recs.return_value = {
        "clarification_needed": False,
        "results": [
            {
                "id": str(uuid.uuid4()),
                "title": "Mock Arcade Game",
                "description": "Mock description",
                "genres": ["Arcade"],
                "platforms": ["PC"],
                "tags": [],
                "release_year": 2024,
                "source": "Mock",
                "match_score": 0.95,
                "match_reason": "Mock reason",
                "is_external": False,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }
    
    return {
        "interpret": mock_interpret,
        "generate": mock_generate,
        "recommend": mock_recs
    }

@pytest.mark.asyncio
async def test_search_endpoint_e2e(mock_gemini):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/search", json={
            "prompt": "A simple bouncing ball game"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["clarification_needed"] is False
        
        # Verify parallel results are merged
        assert len(data["recommendations"]) == 1
        assert data["recommendations"][0]["title"] == "Mock Arcade Game"
        
        assert data["generated_game"] is not None
        assert data["generated_game"]["playable"] is True
        assert data["generated_game"]["html_content"] == "<html><body>Mock Game</body></html>"
        assert "game_id" in data["generated_game"] # Ensure ID was assigned

@pytest.mark.asyncio
async def test_search_endpoint_rate_limit():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Our rate limit is 5/minute. Fire 6 requests.
        responses = []
        for _ in range(6):
            res = await ac.post("/search", json={"prompt": "test limit"})
            responses.append(res)
            
        assert responses[0].status_code == 200
        assert responses[5].status_code == 429
