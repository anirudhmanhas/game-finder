from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from schemas import RecommendationResult, StructuredQuery
from repository import GameRepository
from models import Game

def mock_external_game_search(query: StructuredQuery) -> List[RecommendationResult]:
    """Mock external API call to RAWG or IGDB when internal results are sparse."""
    genre_str = query.genres[0] if query.genres else "Action"
    return [
        RecommendationResult(
            id=uuid4(),
            title=f"{genre_str} Odyssey (External)",
            description=query.intent_summary,
            genres=query.genres,
            platforms=[query.platform_preference] if query.platform_preference else ["PC", "Console"],
            tags=query.mechanics,
            release_year=2025,
            source="mock_igdb",
            external_url="https://igdb.com/mock",
            created_at=datetime.utcnow(),
            match_score=0.85,
            match_reason="Found on external database matching your exact intent.",
            is_external=True
        )
    ]

def _safe_tags(game: Game) -> list:
    """Safely extract tags as a flat list, regardless of DB storage format."""
    tags = game.tags
    if not tags:
        return []
    
    flat_tags = []
    
    def extract_values(item):
        if isinstance(item, list):
            for i in item:
                extract_values(i)
        elif isinstance(item, dict):
            for v in item.values():
                extract_values(v)
        else:
            flat_tags.append(str(item))
            
    extract_values(tags)
    return flat_tags

def calculate_score(game: Game, query: StructuredQuery, user_history: List[str]) -> float:
    score = 0.0
    tags = _safe_tags(game)
    genres = game.genres or []
    
    # 1. Vector similarity bump
    score += 0.4 
    
    # 2. Genre match (heavy weight)
    for genre in query.genres:
        if genre.lower() in [g.lower() for g in genres]:
            score += 0.2
            
    # 3. Mechanics match (medium weight)
    tags_lower = [str(t).lower() for t in tags]
    for mechanic in query.mechanics:
        if mechanic.lower() in tags_lower:
            score += 0.1
            
    # 4. Platform match
    platforms = game.platforms or []
    if query.platform_preference and query.platform_preference.lower() in [p.lower() for p in platforms]:
        score += 0.1
        
    # 5. Personalization bump (history)
    for tag in user_history:
        tag_l = tag.lower()
        if tag_l in [g.lower() for g in genres] or tag_l in tags_lower:
            score += 0.05
            
    return min(1.0, score)

def generate_match_reason(game: Game, query: StructuredQuery, score: float) -> str:
    reasons = []
    genres = game.genres or []
    platforms = game.platforms or []
    
    if any(g.lower() in [gg.lower() for gg in genres] for g in query.genres):
        reasons.append("matches your genre preference")
    if query.platform_preference and query.platform_preference.lower() in [p.lower() for p in platforms]:
        reasons.append("available on your preferred platform")
        
    if not reasons:
        if score > 0.6:
            return "Semantically matches your request."
        return "Broadly fits your intent."
        
    return "This game " + " and ".join(reasons) + "."

async def get_recommendations(query: StructuredQuery, user_id: Optional[str], filters: Optional[dict], db: Session) -> List[RecommendationResult]:
    """
    Get game recommendations based on a pre-parsed StructuredQuery.
    
    Returns a list of RecommendationResult objects (not dicts).
    """
    if query.needs_clarification:
        return []
        
    repo = GameRepository(db)
    user_history = repo.get_user_history(user_id) if user_id else []
    
    # 1. Vector search (top 10 closest)
    candidate_games = []
    if db is not None:
        if query.embedding:
            try:
                candidate_games = repo.search_similar_games(query.embedding, limit=10)
            except Exception as e:
                print(f"Vector search failed, falling back to attribute filter: {e}")
                candidate_games = repo.filter_by_attributes(genre=query.genres[0] if query.genres else None)
        else:
            # Fallback if embedding failed but query parsed
            candidate_games = repo.filter_by_attributes(genre=query.genres[0] if query.genres else None)
        
    # Apply filters if any
    if filters:
        if "genre" in filters and filters["genre"]:
            filter_genres = [f.lower() for f in filters["genre"]]
            candidate_games = [g for g in candidate_games if any(fg in [genre.lower() for genre in (g.genres or [])] for fg in filter_genres)]
        if "multiplayer" in filters and filters["multiplayer"]:
            candidate_games = [g for g in candidate_games if "multiplayer" in [str(t).lower() for t in _safe_tags(g)] or "co-op" in [str(t).lower() for t in _safe_tags(g)]]

    # 2. Score and rank
    scored_results = []
    for game in candidate_games:
        score = calculate_score(game, query, user_history)
        reason = generate_match_reason(game, query, score)
        
        result = RecommendationResult(
            id=game.id,
            title=game.title,
            description=game.description,
            genres=game.genres or [],
            platforms=game.platforms or [],
            tags=_safe_tags(game),
            release_year=game.release_year,
            source=game.source,
            external_url=game.external_url,
            created_at=game.created_at,
            match_score=round(score, 2),
            match_reason=reason,
            is_external=False
        )
        scored_results.append(result)
        
    # Sort by score descending
    scored_results.sort(key=lambda x: x.match_score, reverse=True)
    
    # 3. Check if we need external fallback
    if not scored_results or scored_results[0].match_score < 0.5:
        external_results = mock_external_game_search(query)
        scored_results.extend(external_results)
        scored_results.sort(key=lambda x: x.match_score, reverse=True)
        
    final_results = scored_results[:5]
    
    # 4. Inject AI Popularity
    try:
        from services.prompt_interpreter import generate_popularity_metrics
        game_titles = [r.title for r in final_results]
        pop_metrics = await generate_popularity_metrics(game_titles)
        
        for r in final_results:
            if r.title in pop_metrics:
                r.ai_popularity_score = pop_metrics[r.title].get("score")
                r.ai_popularity_reason = pop_metrics[r.title].get("reason")
    except Exception as e:
        import traceback
        print(f"Error fetching popularity: {e}")
        traceback.print_exc()
        
    return final_results
