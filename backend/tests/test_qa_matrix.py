"""
QA Matrix - 25-prompt breadth & robustness test.
Runs each prompt against the live /search endpoint on localhost:8001
and records whether each pipeline stage behaved correctly.

Usage:
    cd backend
    venv\\Scripts\\python tests\\test_qa_matrix.py

Outputs a JSON report and a human-readable summary.
"""
import json
import time
import urllib.request
import urllib.error
import sys
import os

API = "http://127.0.0.1:8001"

# -- 25 Diverse Prompts ------------------------------------------------
PROMPTS = [
    # --- Short & clear ---
    {"id": 1,  "prompt": "2D platformer game with jumping",         "category": "short-clear",      "expect_clarify": False, "expect_genre": "Platformer"},
    {"id": 2,  "prompt": "space shooter with aliens",               "category": "short-clear",      "expect_clarify": False, "expect_genre": "Shooter"},
    {"id": 3,  "prompt": "puzzle game with block matching",         "category": "short-clear",      "expect_clarify": False, "expect_genre": "Puzzle"},
    # --- Long & descriptive ---
    {"id": 4,  "prompt": "A cozy pixel-art farming game where I can grow crops, raise animals, and decorate my house",
                                                                    "category": "long-descriptive", "expect_clarify": False, "expect_genre": "Simulation"},
    {"id": 5,  "prompt": "An intense dark sci-fi roguelike with permadeath, procedural dungeons, and difficult boss fights",
                                                                    "category": "long-descriptive", "expect_clarify": False, "expect_genre": "Action"},
    # --- Multi-genre ---
    {"id": 6,  "prompt": "RPG with strategy elements and puzzle mechanics",
                                                                    "category": "multi-genre",      "expect_clarify": False, "expect_genre": "RPG"},
    {"id": 7,  "prompt": "racing game with action combat and powerups",
                                                                    "category": "multi-genre",      "expect_clarify": False, "expect_genre": "Racing"},
    # --- Platform-specific ---
    {"id": 8,  "prompt": "a mobile puzzle game I can play on my phone",
                                                                    "category": "platform-specific","expect_clarify": False, "expect_genre": "Puzzle"},
    {"id": 9,  "prompt": "Nintendo Switch party game for 4 players",
                                                                    "category": "platform-specific","expect_clarify": False, "expect_genre": None},
    # --- Tone / mood ---
    {"id": 10, "prompt": "a relaxing game with no combat, just exploring nature",
                                                                    "category": "tone-mood",        "expect_clarify": False, "expect_genre": None},
    {"id": 11, "prompt": "a horror survival game that is genuinely scary",
                                                                    "category": "tone-mood",        "expect_clarify": False, "expect_genre": None},
    # --- Vague (should ask for clarification) ---
    {"id": 12, "prompt": "a fun game",                              "category": "vague",            "expect_clarify": True,  "expect_genre": None},
    {"id": 13, "prompt": "something to play",                       "category": "vague",            "expect_clarify": True,  "expect_genre": None},
    # --- Off-topic / nonsensical (should ask for clarification) ---
    {"id": 14, "prompt": "what is the weather today",               "category": "off-topic",        "expect_clarify": True,  "expect_genre": None},
    {"id": 15, "prompt": "asdfghjkl qwerty",                        "category": "nonsensical",      "expect_clarify": True,  "expect_genre": None},
    # --- Feasibility edge-cases (should NOT generate) ---
    {"id": 16, "prompt": "a massive open-world 3D MMO RPG with thousands of players",
                                                                    "category": "infeasible",       "expect_clarify": False, "expect_genre": "RPG"},
    {"id": 17, "prompt": "a realistic VR flight simulator",         "category": "infeasible",       "expect_clarify": False, "expect_genre": None},
    # --- Feasibility edge-cases (SHOULD generate) ---
    {"id": 18, "prompt": "a simple brick breaker game with paddle and bricks",
                                                                    "category": "feasible",         "expect_clarify": False, "expect_genre": "Arcade"},
    {"id": 19, "prompt": "a snake game where the snake grows when eating food",
                                                                    "category": "feasible",         "expect_clarify": False, "expect_genre": "Arcade"},
    # --- Specific mechanics ---
    {"id": 20, "prompt": "turn-based tactical combat like chess but with fantasy characters",
                                                                    "category": "specific-mechanic","expect_clarify": False, "expect_genre": "Strategy"},
    {"id": 21, "prompt": "a rhythm game where you tap in time with music beats",
                                                                    "category": "specific-mechanic","expect_clarify": False, "expect_genre": None},
    # --- Non-English (best effort) ---
    {"id": 22, "prompt": "un jeu de plateforme simple en 2D",       "category": "non-english",      "expect_clarify": False, "expect_genre": "Platformer"},
    {"id": 23, "prompt": "un juego de puzzle simple",               "category": "non-english",      "expect_clarify": False, "expect_genre": "Puzzle"},
    # --- Edge: very long prompt ---
    {"id": 24, "prompt": "I want a game that combines elements of classic arcade shooters from the 80s like Galaga and Space Invaders with modern indie pixel art aesthetics, chiptune music, and a progression system where you unlock new ships and weapons over time. It should be playable in the browser with keyboard controls and have a leaderboard.",
                                                                    "category": "very-long",        "expect_clarify": False, "expect_genre": "Shooter"},
    # --- Edge: HTML injection attempt ---
    {"id": 25, "prompt": "<script>alert('xss')</script> give me a platformer game",
                                                                    "category": "injection",        "expect_clarify": False, "expect_genre": None},
]


def call_search(prompt, timeout=90):
    """POST to /search and return the JSON response or an error dict."""
    try:
        body = json.dumps({"prompt": prompt}).encode("utf-8")
        req = urllib.request.Request(
            f"{API}/search",
            data=body,
            headers={"Content-Type": "application/json", "User-Agent": "QA-Bot"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"status": resp.status, "body": json.loads(resp.read())}
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            err_body = ""
        return {"status": e.code, "body": None, "error": f"{e} | {err_body}"}
    except Exception as e:
        return {"status": 0, "body": None, "error": str(e)}


def evaluate(case, response):
    """Score a single test case against the API response."""
    result = {
        "id": case["id"],
        "prompt": case["prompt"],
        "category": case["category"],
        "http_ok": False,
        "clarify_correct": False,
        "genres_found": [],
        "genre_match": None,
        "num_recommendations": 0,
        "has_generated_game": False,
        "generated_game_playable": False,
        "notes": [],
    }

    if response["status"] != 200:
        result["notes"].append("HTTP %d: %s" % (response["status"], response.get("error", "")))
        return result

    body = response["body"]
    result["http_ok"] = True

    # --- Clarification check ---
    got_clarify = body.get("clarification_needed", False)
    result["clarify_correct"] = got_clarify == case["expect_clarify"]
    if not result["clarify_correct"]:
        if case["expect_clarify"]:
            result["notes"].append("SHOULD have asked for clarification but didn't")
        else:
            q = body.get("suggested_question", "")
            result["notes"].append("Unexpectedly asked for clarification: %s" % q)

    # --- Recommendations ---
    recs = body.get("recommendations", [])
    result["num_recommendations"] = len(recs)
    if recs:
        result["genres_found"] = list(set(g for r in recs for g in r.get("genres", [])))

    expected = case.get("expect_genre")
    if expected and recs:
        match = any(expected.lower() in [g.lower() for g in r.get("genres", [])] for r in recs)
        result["genre_match"] = match
        if not match:
            result["notes"].append("Expected genre '%s' not in results" % expected)

    # --- Generation ---
    gen = body.get("generated_game")
    if gen:
        result["has_generated_game"] = True
        result["generated_game_playable"] = gen.get("playable", False)

    return result


def main():
    print("")
    print("=" * 70)
    print("  PlayWeave QA Matrix -- 25 Prompt Breadth Test")
    print("=" * 70)
    print("")

    results = []
    pass_count = 0
    fail_count = 0

    for i, case in enumerate(PROMPTS):
        label = "[%2d/%d]" % (case["id"], len(PROMPTS))
        prompt_short = case["prompt"][:55]
        sys.stdout.write("%s  %-18s  %-55s  " % (label, case["category"], prompt_short))
        sys.stdout.flush()

        t0 = time.time()
        resp = call_search(case["prompt"])
        elapsed = time.time() - t0

        ev = evaluate(case, resp)
        ev["elapsed_s"] = round(elapsed, 2)

        is_pass = ev["http_ok"] and ev["clarify_correct"]
        ev["verdict"] = "PASS" if is_pass else "FAIL"

        if is_pass:
            pass_count += 1
            gen_flag = "Y" if ev["generated_game_playable"] else "N"
            print("  PASS  (%.1fs)  recs=%d  gen=%s" % (elapsed, ev["num_recommendations"], gen_flag))
        else:
            fail_count += 1
            notes = "; ".join(ev["notes"]) or "see details"
            print("  FAIL  (%.1fs)  %s" % (elapsed, notes))

        results.append(ev)

        # Pause every 8 requests to be safe with 30/minute rate limit
        if (i + 1) % 8 == 0 and (i + 1) < len(PROMPTS):
            print("        ... pausing 10s ...")
            time.sleep(10)

    # -- Summary -------------------------------------------------------
    print("")
    print("=" * 70)
    print("  RESULTS:  %d PASS / %d FAIL / %d TOTAL" % (pass_count, fail_count, len(PROMPTS)))
    print("=" * 70)

    if fail_count:
        print("")
        print("  FAILURES:")
        for r in results:
            if r["verdict"] == "FAIL":
                print("    #%2d [%s] %s" % (r["id"], r["category"], r["prompt"][:50]))
                for n in r["notes"]:
                    print("         -> %s" % n)

    # Save JSON report
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qa_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print("")
    print("  Full JSON report saved to: %s" % report_path)


if __name__ == "__main__":
    main()
