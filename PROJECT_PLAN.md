# Project Plan: AI-Powered Game Discovery and Generation Platform

## 1. Proposed Architecture

Our platform will consist of five main components working together to deliver a seamless game discovery and generation experience:

- **Frontend (Web App):** A responsive user interface where users can input natural language prompts, view personalized game recommendations, and play generated games directly in the browser.
- **Backend (API Gateway & Orchestrator):** The core server that routes requests, handles authentication, orchestrates LLM calls, and manages asynchronous tasks like game generation.
- **Database (Relational & Cache):** Stores game metadata, user profiles, prompt history, and generated game states.
- **LLM Integration:** External API for natural language understanding (NLU) to parse user prompts and extract intents, and to generate code/logic for simple games.
- **Game Generation Engine:** A secure sandbox or wrapper (e.g., Phaser.js or basic HTML5 Canvas) that interprets LLM-generated code into playable web games.

## 2. Tech Stack Recommendation

- **Frontend:** **React + Vite** (Fast build times, excellent ecosystem for web games/Canvas integration). *Styling:* Tailwind CSS.
- **Backend:** **FastAPI (Python)** (High performance, native async support for LLM calls, excellent OpenAPI documentation).
- **Database:** **PostgreSQL** (Robust relational data, JSONB support for flexible game tags/mechanics). *Caching/Message Broker:* **Redis** (for Celery and LLM response caching).
- **Task Queue:** **Celery** (Crucial for handling long-running game generation tasks asynchronously).
- **LLM API:** **Google Gemini API** (State-of-the-art NLP and code generation capabilities).
- **Game Engine:** **Phaser.js** (Best-in-class 2D HTML5 game framework, easy to target with LLM code generation).

*Justification:* This stack balances rapid development (FastAPI, React) with the performance needed for asynchronous AI tasks (Celery, Redis) and flexible data modeling (PostgreSQL JSONB).

## 3. Data Model

Below are the primary entities for the PostgreSQL database:

**`users`**
- `id` (UUID, Primary Key)
- `username` (String, Unique)
- `email` (String, Unique)
- `created_at` (Timestamp)

**`games` (Existing game database)**
- `id` (UUID, Primary Key)
- `title` (String)
- `description` (Text)
- `genre` (Array of Strings)
- `platform` (Array of Strings)
- `tags` (Array of Strings - e.g., "sci-fi", "retro")
- `mechanics` (Array of Strings)
- `multiplayer_support` (Boolean)
- `difficulty` (String / Enum)
- `source_url` (String)

**`prompts`**
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key)
- `raw_text` (Text)
- `parsed_intent` (JSONB - extracted genres, tags, mechanics)
- `created_at` (Timestamp)

**`generated_games`**
- `id` (UUID, Primary Key)
- `prompt_id` (UUID, Foreign Key)
- `status` (Enum - PENDING, GENERATING, COMPLETED, FAILED)
- `source_code` (Text - the generated game logic)
- `assets` (JSONB - URLs to generated or default assets)
- `created_at` (Timestamp)

## 4. Phased Build Plan

1. **Phase 1: Architecture & Scaffolding** (Current)
   - Define project plan, scaffold repo structure (Frontend, Backend, Docker).
2. **Phase 2: Data Layer & Basic Backend**
   - Setup PostgreSQL models, Alembic migrations, and basic CRUD endpoints in FastAPI.
3. **Phase 3: NLP & Prompt Understanding**
   - Integrate LLM API. Build the pipeline to parse raw text into structured `parsed_intent` JSON.
4. **Phase 4: Recommendation Engine**
   - Populate `games` table with sample data. Build similarity search to match `parsed_intent` to existing games.
5. **Phase 5: Game Generation Engine MVP**
   - Setup Celery workers. Engineer LLM prompts to output valid Phaser.js/Canvas code based on user requests.
6. **Phase 6: Frontend Development**
   - Build React UI for inputting prompts, displaying recommendations, and a secure `<iframe>` or sandbox component to run generated games.
7. **Phase 7: Integration, Testing & Deployment**
   - End-to-end testing, error handling, Docker optimizations, and cloud deployment (e.g., AWS, GCP).

## 5. Key Risks

- **LLM Latency & Cost:** Parsing and especially generating game code can be slow and expensive. *Mitigation:* Heavy caching, async progress bars for the user, and streaming responses.
- **Generated Game Quality & Scope Limits:** Generative AI for games is experimental. Generated games may have bugs, lack "fun", or fail to compile. *Mitigation:* Restrict scope to simple 2D genres initially (e.g., pong, simple platformers, space shooters) and provide robust error handling/fallback templates.
- **Security (XSS / Arbitrary Code Execution):** Running LLM-generated code in the browser is risky. *Mitigation:* Execute generated games in highly restricted sandboxes or cross-origin `<iframe>`s.
- **Data Licensing:** Scraping or acquiring a database of existing games might violate terms of service. *Mitigation:* Use open APIs (like IGDB or RAWG) and comply with their licensing and attribution requirements.
