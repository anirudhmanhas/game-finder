import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure backend directory is in path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.prompt_interpreter import interpret_prompt

@patch('services.prompt_interpreter.genai.embed_content')
@patch('services.prompt_interpreter.genai.GenerativeModel')
def test_interpret_clear_genre_specific_prompt(mock_generative_model_class, mock_embed_content):
    # Setup mock
    mock_model_instance = MagicMock()
    mock_generative_model_class.return_value = mock_model_instance
    
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "genres": ["Shooter", "Action"],
        "sub_genres": ["Sci-Fi"],
        "mechanics": ["First-Person"],
        "platform_preference": "PC",
        "multiplayer_support": True,
        "tone": "Dark",
        "intent_summary": "Looking for a multiplayer sci-fi shooter on PC.",
        "needs_clarification": False,
        "suggested_question": None
    })
    mock_model_instance.generate_content.return_value = mock_response
    
    mock_embed_content.return_value = {"embedding": [0.1, 0.2, 0.3]}

    # Execute
    prompt = "A multiplayer sci-fi shooter on PC"
    result = interpret_prompt(prompt)

    # Assert
    assert result.genres == ["Shooter", "Action"]
    assert result.platform_preference == "PC"
    assert result.multiplayer_support is True
    assert result.needs_clarification is False
    assert result.embedding == [0.1, 0.2, 0.3]
    mock_model_instance.generate_content.assert_called_once_with(prompt)
    mock_embed_content.assert_called_once()


@patch('services.prompt_interpreter.genai.GenerativeModel')
def test_interpret_vague_prompt(mock_generative_model_class):
    # Setup mock
    mock_model_instance = MagicMock()
    mock_generative_model_class.return_value = mock_model_instance
    
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "genres": [],
        "sub_genres": [],
        "mechanics": [],
        "platform_preference": None,
        "multiplayer_support": None,
        "tone": None,
        "intent_summary": "Vague request for a game.",
        "needs_clarification": True,
        "suggested_question": "What kind of game are you in the mood for? Action, puzzle, relaxing?"
    })
    mock_model_instance.generate_content.return_value = mock_response

    # Execute
    prompt = "A fun game"
    result = interpret_prompt(prompt)

    # Assert
    assert result.needs_clarification is True
    assert result.suggested_question is not None
    assert result.embedding is None # Should not call embedding if clarification is needed


@patch('services.prompt_interpreter.genai.embed_content')
@patch('services.prompt_interpreter.genai.GenerativeModel')
def test_interpret_mixed_genres_prompt(mock_generative_model_class, mock_embed_content):
    # Setup mock
    mock_model_instance = MagicMock()
    mock_generative_model_class.return_value = mock_model_instance
    
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "genres": ["Strategy", "Racing"],
        "sub_genres": [],
        "mechanics": ["Resource Management"],
        "platform_preference": None,
        "multiplayer_support": None,
        "tone": "Relaxing",
        "intent_summary": "Looking for a relaxing strategy racing game.",
        "needs_clarification": False,
        "suggested_question": None
    })
    mock_model_instance.generate_content.return_value = mock_response
    mock_embed_content.return_value = {"embedding": [0.5, 0.5]}

    # Execute
    prompt = "A relaxing strategy racing game"
    result = interpret_prompt(prompt)

    # Assert
    assert "Strategy" in result.genres
    assert "Racing" in result.genres
    assert result.tone == "Relaxing"
    assert result.needs_clarification is False


@patch('services.prompt_interpreter.genai.GenerativeModel')
def test_interpret_no_gaming_content_prompt(mock_generative_model_class):
    # Setup mock
    mock_model_instance = MagicMock()
    mock_generative_model_class.return_value = mock_model_instance
    
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "genres": [],
        "sub_genres": [],
        "mechanics": [],
        "platform_preference": None,
        "multiplayer_support": None,
        "tone": None,
        "intent_summary": "Not a gaming query.",
        "needs_clarification": True,
        "suggested_question": "I am a game recommendation AI. Could you describe a game you'd like to play?"
    })
    mock_model_instance.generate_content.return_value = mock_response

    # Execute
    prompt = "What's the weather like today?"
    result = interpret_prompt(prompt)

    # Assert
    assert result.needs_clarification is True
    assert result.embedding is None
