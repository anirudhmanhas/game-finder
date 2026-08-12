import uuid
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from pgvector.sqlalchemy import Vector
from database import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    genres = Column(ARRAY(String), default=list)
    platforms = Column(ARRAY(String), default=list)
    tags = Column(JSONB, default=list)
    release_year = Column(Integer, nullable=True)
    source = Column(String, nullable=True)
    external_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    embedding = Column(Vector(768), nullable=True)  # Using 768 for Gemini text-embedding-004 size compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class GeneratedGame(Base):
    __tablename__ = "generated_games"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    prompt = Column(Text, nullable=False)
    html_content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserLike(Base):
    __tablename__ = "user_likes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(String, index=True, nullable=False)
    game_id = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AnalyticsLog(Base):
    __tablename__ = "analytics_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(String, index=True, nullable=True)
    prompt = Column(Text, nullable=False)
    generation_attempted = Column(Boolean, default=False)
    generated_game_id = Column(String, nullable=True)
    clarification_needed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
