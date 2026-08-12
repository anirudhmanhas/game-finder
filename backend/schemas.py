from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime

class GameBase(BaseModel):
    title: str
    description: Optional[str] = None
    genres: List[str] = []
    platforms: List[str] = []
    tags: List[str] = []
    release_year: Optional[int] = None
    source: Optional[str] = None
    external_url: Optional[str] = None

class GameCreate(GameBase):
    pass

class GameResponse(GameBase):
    id: UUID
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class StructuredQuery(BaseModel):
    genres: List[str] = []
    sub_genres: List[str] = []
    mechanics: List[str] = []
    platform_preference: Optional[str] = None
    multiplayer_support: Optional[bool] = None
    tone: Optional[str] = None
    intent_summary: str
    embedding: Optional[List[float]] = None
    needs_clarification: bool = False
    suggested_question: Optional[str] = None

class RecommendationRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = None
    filters: Optional[dict] = None

class RecommendationResult(GameResponse):
    match_score: float
    match_reason: str
    is_external: bool = False

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    playable: bool
    game_id: Optional[UUID] = None
    html_content: Optional[str] = None
    reason_if_not_playable: Optional[str] = None

class SearchRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = None
    filters: Optional[dict] = None

class SearchResponse(BaseModel):
    clarification_needed: bool
    suggested_question: Optional[str] = None
    recommendations: List[RecommendationResult] = []
    generated_game: Optional[GenerateResponse] = None
