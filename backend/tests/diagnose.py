"""Diagnose the 500 error by calling each pipeline stage directly."""
import os, sys, json, traceback
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/gamefinder"

from dotenv import load_dotenv
load_dotenv()

print("=== Stage 1: Prompt Interpreter ===")
try:
    from services.prompt_interpreter import interpret_prompt
    query = interpret_prompt("a 2D platformer game with pixel art and jumping on PC")
    print(f"  needs_clarification: {query.needs_clarification}")
    print(f"  genres: {query.genres}")
    print(f"  mechanics: {query.mechanics}")
    print(f"  embedding length: {len(query.embedding) if query.embedding else 'None'}")
    print(f"  intent_summary: {query.intent_summary}")
    print("  --> PASS")
except Exception as e:
    print(f"  --> FAIL: {e}")
    traceback.print_exc()
    sys.exit(1)

if query.needs_clarification:
    print("\n  Prompt triggered clarification, stopping here.")
    sys.exit(0)

print("\n=== Stage 2: Database Connection ===")
try:
    from database import SessionLocal
    db = SessionLocal()
    from models import Game
    count = db.query(Game).count()
    print(f"  Game count in DB: {count}")
    print("  --> PASS")
except Exception as e:
    print(f"  --> FAIL: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n=== Stage 3: Recommendation Service ===")
try:
    from services.recommendation import get_recommendations
    recs = get_recommendations(query, None, None, db)
    print(f"  Returned {len(recs)} recommendations")
    print(f"  Type: {type(recs)}")
    if recs:
        r = recs[0]
        print(f"  First rec type: {type(r)}")
        print(f"  First rec title: {r.title}")
        print(f"  First rec id type: {type(r.id)}")
    print("  --> PASS")
except Exception as e:
    print(f"  --> FAIL: {e}")
    traceback.print_exc()

print("\n=== Stage 4: Pydantic Serialization ===")
try:
    from schemas import SearchResponse, RecommendationResult
    resp = SearchResponse(
        clarification_needed=False,
        recommendations=recs,
        generated_game=None
    )
    dumped = resp.model_dump()
    print(f"  model_dump keys: {list(dumped.keys())}")
    print(f"  recs count in dump: {len(dumped['recommendations'])}")
    json_str = json.dumps(dumped, default=str)
    print(f"  JSON length: {len(json_str)}")
    print("  --> PASS")
except Exception as e:
    print(f"  --> FAIL: {e}")
    traceback.print_exc()

print("\n=== Stage 5: Game Generation Feasibility ===")
try:
    from services.game_generator import check_feasibility
    feasible, reason = check_feasibility(query)
    print(f"  Feasible: {feasible}, Reason: {reason}")
    print("  --> PASS")
except Exception as e:
    print(f"  --> FAIL: {e}")
    traceback.print_exc()

db.close()
print("\n=== ALL STAGES COMPLETE ===")
