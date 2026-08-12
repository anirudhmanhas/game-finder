from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
import asyncio
import re
import html
import traceback
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("playweave.api")

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.exceptions import ResponseValidationError

from database import get_db
from schemas import SearchRequest, SearchResponse, GenerateResponse
from services.recommendation import get_recommendations
from services.game_generator import generate_game_pipeline
from services.prompt_interpreter import interpret_prompt
from models import GeneratedGame, UserLike, AnalyticsLog

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Game Finder & Generator API",
    description="API for parsing game prompts, finding recommendations, and generating mini-games.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
    print(f"RESPONSE VALIDATION ERROR: {exc.errors()}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: Data serialization failed. {exc.errors()}"}
    )

import os

frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
allow_origins = [url.strip() for url in frontend_url.split(",")] if frontend_url else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def sanitize_prompt(prompt: str) -> str:
    clean = re.sub(r'<[^>]*>', '', prompt)
    clean = html.unescape(clean)
    return clean[:500].strip()

@app.get("/")
async def root():
    return {"message": "Welcome to the Game Finder API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/search", response_model=SearchResponse)
@limiter.limit("30/minute")
async def search_games(request: Request, req: SearchRequest, db: Session = Depends(get_db)):
    try:
        start_time = time.time()
        sanitized_prompt = sanitize_prompt(req.prompt)
        
        # 1. Prompt Understanding (single call — result reused everywhere)
        t0 = time.time()
        query = await interpret_prompt(sanitized_prompt)
        logger.info(f"[TIMING] interpret_prompt took {time.time() - t0:.2f}s")
        
        # 2. Check for clarification
        if query.needs_clarification:
            try:
                log = AnalyticsLog(
                    user_id=req.user_id,
                    prompt=sanitized_prompt,
                    clarification_needed=True
                )
                db.add(log)
                db.commit()
            except Exception:
                if db:
                    db.rollback()
                
            return SearchResponse(
                clarification_needed=True,
                suggested_question=query.suggested_question
            )
            
        # 3. Get recommendations (synchronous — fast, no Playwright)
        recs = []
        try:
            recs = get_recommendations(query, req.user_id, req.filters, db)
        except Exception as e:
            print(f"Recommendation error (non-fatal): {e}")
            traceback.print_exc()
        
        # 4. Attempt game generation (async with timeout)
        gen_result = None
        gen_attempted = False
        
        try:
            gen_attempted = True
            t1 = time.time()
            gen_result_dict = await asyncio.wait_for(
                generate_game_pipeline(sanitized_prompt, query),
                timeout=60.0
            )
            logger.info(f"[TIMING] generate_game_pipeline took {time.time() - t1:.2f}s")
            
            if gen_result_dict and gen_result_dict.get("playable") and gen_result_dict.get("html_content"):
                if db:
                    new_game = GeneratedGame(
                        prompt=sanitized_prompt,
                        html_content=gen_result_dict["html_content"]
                    )
                    db.add(new_game)
                    db.commit()
                    db.refresh(new_game)
                    gen_result_dict["game_id"] = str(new_game.id)
                gen_result = GenerateResponse(**gen_result_dict)
        except asyncio.TimeoutError:
            print("Generation timed out after 60s.")
        except Exception as e:
            print(f"Generation failed: {e}")
            traceback.print_exc()
            
        # 5. Log Analytics
        try:
            log = AnalyticsLog(
                user_id=req.user_id,
                prompt=sanitized_prompt,
                generation_attempted=gen_attempted,
                generated_game_id=str(gen_result.game_id) if gen_result and gen_result.game_id else None,
                clarification_needed=False
            )
            if db:
                db.add(log)
                db.commit()
        except Exception:
            if db:
                db.rollback()
        
        logger.info(f"Total Search Latency: {time.time() - start_time:.2f}s")
        return SearchResponse(
            clarification_needed=False,
            recommendations=recs,
            generated_game=gen_result
        )
    except Exception as e:
        print(f"SEARCH ENDPOINT ERROR: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal error: {str(e)}"}
        )

@app.get("/games/{game_id}/play")
async def play_game(game_id: str, db: Session = Depends(get_db)):
    game = db.query(GeneratedGame).filter(GeneratedGame.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return HTMLResponse(content=game.html_content)

@app.post("/games/{game_id}/like")
async def like_game(game_id: str, user_id: str, db: Session = Depends(get_db)):
    like = UserLike(user_id=user_id, game_id=game_id)
    db.add(like)
    db.commit()
    return {"status": "success"}
