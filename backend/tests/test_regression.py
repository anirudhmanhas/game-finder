import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app
from schemas import StructuredQuery
from services.prompt_interpreter import interpret_prompt

client = TestClient(app)

@patch('main.get_recommendations')
@patch('main.interpret_prompt', new_callable=AsyncMock)
def test_rate_limit(mock_interpret, mock_get_recs):
    """Verify that the 30/minute rate limit is enforced."""
    mock_get_recs.return_value = []
    mock_interpret.return_value = StructuredQuery(
        intent_summary="test",
        genres=["Action"],
        platform_preference="PC",
        needs_clarification=False
    )
    
    responses = []
    for _ in range(35):
        resp = client.post("/search", json={"prompt": "rate limit test"}, headers={"X-Forwarded-For": "10.0.0.1"})
        responses.append(resp.status_code)
        
    # At least one response should be 429
    assert 429 in responses, f"Rate limit was not enforced (expected 429 status code). Got: {responses}"


@patch('main.get_recommendations')
@patch('main.interpret_prompt', new_callable=AsyncMock)
def test_invalid_serialization_handled(mock_interpret, mock_get_recs):
    """
    Verify that if somehow an invalid prompt or result is generated, 
    the API handles it gracefully instead of returning a raw 500 without a body.
    """
    # Mocking get_recommendations to return something that breaks ResponseValidationError
    mock_get_recs.return_value = [{"invalid_dict_instead_of_model": True}]
    
    mock_interpret.return_value = StructuredQuery(
        intent_summary="puzzle",
        genres=["Puzzle"],
        mechanics=["matching"],
        needs_clarification=False
    )
    
    resp = client.post("/search", json={"prompt": "puzzle game with block matching"}, headers={"X-Forwarded-For": "10.0.0.2"})
    assert resp.status_code in [200, 500]
    
    if resp.status_code == 500:
        data = resp.json()
        assert "detail" in data, "500 error should have a structured detail message, not raw string"
    else:
        data = resp.json()
        assert "clarification_needed" in data
