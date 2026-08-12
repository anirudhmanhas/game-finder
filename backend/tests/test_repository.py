import pytest
from unittest.mock import MagicMock
from repository import GameRepository
from models import Game
from schemas import GameCreate

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def repository(mock_db_session):
    return GameRepository(mock_db_session)

def test_get_by_id(repository, mock_db_session):
    game_id = "test-uuid"
    expected_game = Game(id=game_id, title="Test Game")
    
    # Setup mock chain: db.query().filter().first()
    mock_db_session.query.return_value.filter.return_value.first.return_value = expected_game
    
    result = repository.get_by_id(game_id)
    
    assert result == expected_game
    mock_db_session.query.assert_called_once_with(Game)

def test_create_game(repository, mock_db_session):
    game_data = GameCreate(title="New Game", genres=["RPG"])
    
    repository.create(game_data)
    
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

def test_search_by_keyword(repository, mock_db_session):
    expected_games = [Game(title="Space Quest"), Game(title="Space Odyssey")]
    
    # Setup mock chain
    mock_db_session.query.return_value.filter.return_value.all.return_value = expected_games
    
    result = repository.search_by_keyword("Space")
    
    assert result == expected_games
    mock_db_session.query.assert_called_once_with(Game)

def test_filter_by_attributes(repository, mock_db_session):
    expected_games = [Game(title="RPG Game", genres=["RPG"])]
    
    # Setup mock chain
    mock_db_session.query.return_value.filter.return_value.all.return_value = expected_games
    
    result = repository.filter_by_attributes(genre="RPG")
    
    assert result == expected_games
    mock_db_session.query.assert_called_once_with(Game)
