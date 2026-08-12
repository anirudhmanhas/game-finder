from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from models import Game
from schemas import GameCreate

class GameRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, game_id: str) -> Optional[Game]:
        return self.db.query(Game).filter(Game.id == game_id).first()

    def create(self, game_data: GameCreate) -> Game:
        db_game = Game(**game_data.model_dump())
        self.db.add(db_game)
        self.db.commit()
        self.db.refresh(db_game)
        return db_game
        
    def search_by_keyword(self, keyword: str) -> List[Game]:
        search = f"%{keyword}%"
        return self.db.query(Game).filter(
            or_(
                Game.title.ilike(search),
                Game.description.ilike(search)
            )
        ).all()

    def filter_by_attributes(self, genre: Optional[str] = None, platform: Optional[str] = None) -> List[Game]:
        query = self.db.query(Game)
        if genre:
            query = query.filter(Game.genres.any(genre))
        if platform:
            query = query.filter(Game.platforms.any(platform))
        return query.all()

    def search_similar_games(self, query_embedding: list[float], limit: int = 5) -> List[Game]:
        # Uses pgvector's cosine distance operator
        return self.db.query(Game).order_by(Game.embedding.cosine_distance(query_embedding)).limit(limit).all()
        
    def get_user_history(self, user_id: str) -> List[str]:
        # Placeholder for fetching user history.
        # In a real app, this would query a user_game_history table.
        # We return a mock list of liked genres/tags based on the user_id.
        return ["Action", "Sci-Fi"]
