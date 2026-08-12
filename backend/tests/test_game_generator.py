import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import StructuredQuery
from services.game_generator import check_feasibility, generate_game_pipeline

def test_check_feasibility():
    # 1. Unfeasible complex game
    query_unfeasible = StructuredQuery(
        genres=["RPG", "MMO"],
        intent_summary="test",
        multiplayer_support=True
    )
    is_feasible, reason = check_feasibility(query_unfeasible)
    assert is_feasible is False
    assert "multiplayer" in reason.lower()

    # 2. Feasible simple game
    query_feasible = StructuredQuery(
        genres=["Puzzle"],
        intent_summary="test",
        multiplayer_support=False
    )
    is_feasible2, reason2 = check_feasibility(query_feasible)
    assert is_feasible2 is True

@pytest.mark.asyncio
@patch('services.game_generator.validate_game')
@patch('services.game_generator.generate_game_code')
async def test_generate_pipeline_success(mock_generate, mock_validate):
    mock_generate.return_value = "<html><body><canvas></canvas></body></html>"
    # Returns (is_valid, error_msg)
    mock_validate.return_value = (True, None)

    query = StructuredQuery(genres=["Arcade"], intent_summary="A simple arcade game")
    result = await generate_game_pipeline("make a game", query)
    
    assert result["playable"] is True
    assert result["html_content"] is not None
    mock_generate.assert_called_once()
    mock_validate.assert_called_once()

@pytest.mark.asyncio
@patch('services.game_generator.validate_game')
@patch('services.game_generator.generate_game_code')
async def test_generate_pipeline_retry(mock_generate, mock_validate):
    mock_generate.side_effect = ["<html>syntax error</html>", "<html>fixed</html>"]
    # First time fails, second time succeeds
    mock_validate.side_effect = [(False, "SyntaxError"), (True, None)]

    query = StructuredQuery(genres=["Puzzle"], intent_summary="A simple puzzle game")
    result = await generate_game_pipeline("make a game", query)
    
    assert result["playable"] is True
    assert result["html_content"] == "<html>fixed</html>"
    assert mock_generate.call_count == 2
    assert mock_validate.call_count == 2
