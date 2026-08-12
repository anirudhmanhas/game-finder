# Project Plan: AI-Powered Game Discovery and Generation Platform (COMPLETED)

## 1. Final Architecture

Our platform consists of four main components working together to deliver a seamless game discovery and generation experience:

- **Frontend (Web App):** A responsive React interface featuring a minimalist, information-dense UI. Users can input natural language prompts, view personalized game recommendations with AI-generated popularity metrics, and play generated games directly in the browser.
- **Backend (API Gateway & Orchestrator):** A FastAPI server that routes requests, orchestrates Gemini LLM calls via `asyncio`, and manages the pipeline for both semantic search and on-the-fly game generation.
- **Database (Relational & Vector):** A PostgreSQL database using `pgvector` to store game metadata and perform semantic similarity searches against user prompts.
- **LLM Integration (Google Gemini):** Utilizes `gemini-flash-lite-latest` for zero-shot natural language understanding (extracting structured intent from prompts) and generating functional HTML5 Canvas game code.

## 2. Tech Stack Used

- **Frontend:** **React + Vite** (Fast build times, excellent ecosystem for web games/Canvas integration). *Styling:* Vanilla CSS for a custom, premium look without heavy frameworks.
- **Backend:** **FastAPI (Python)** (High performance, native async support for LLM calls).
- **Database:** **PostgreSQL + pgvector** (Robust relational data combined with powerful vector embeddings for semantic search).
- **LLM API:** **Google Gemini API** (State-of-the-art NLP and code generation capabilities).
- **Validation Engine:** **Playwright** (Headless browser automation to sandbox and verify generated game code before presenting it to the user).

## 3. Data Model

**`games` (Game database)**
- `id` (UUID, Primary Key)
- `title` (String)
- `description` (Text)
- `genres` (Array of Strings)
- `platforms` (Array of Strings)
- `tags` (Array of Strings)
- `embedding` (Vector - pgvector for semantic search)
- `image_url` (String)
- `source` (String)

**`generated_games`**
- `id` (UUID, Primary Key)
- `prompt` (Text)
- `html_content` (Text - the generated game logic)
- `is_valid` (Boolean - passed Playwright validation)
- `created_at` (Timestamp)

**`analytics_logs`**
- `id` (Integer, Primary Key)
- `event_type` (String)
- `event_data` (JSON)
- `created_at` (Timestamp)

## 4. Phased Build Plan (All Phases Complete)

- [x] **Phase 1: Architecture & Scaffolding** 
- [x] **Phase 2: Data Layer & Basic Backend** (Setup PostgreSQL models, Alembic migrations)
- [x] **Phase 3: NLP & Prompt Understanding** (Integrate Gemini API for structured intent parsing)
- [x] **Phase 4: Recommendation Engine** (Implement pgvector similarity search, seed DB with 200 games)
- [x] **Phase 5: Game Generation Engine** (Engineer Gemini prompts to output valid HTML5 Canvas code, implement Playwright validation)
- [x] **Phase 6: Frontend Development** (Build React UI, implement "Made by Boiler_Plate_Dine" footer, and Minimalist UI pivot)
- [x] **Phase 7: Dynamic Features** (Add real-time AI popularity metrics to search results)
- [x] **Phase 8: Deployment** (Deploy to Render.com using Infrastructure as Code blueprints, implement `/seed` backdoor for production DB seeding)

## 5. Key Risks Mitigated

- **LLM Latency & Cost:** Mitigated by using `gemini-flash-lite-latest` which provides sub-second reasoning and utilizing native `asyncio.to_thread` to prevent blocking the FastAPI event loop.
- **Generated Game Quality:** Mitigated by implementing a robust headless Chromium (Playwright) validation step that ensures the LLM's output is syntactically valid and renders a functional `<canvas>` before saving it to the database.
- **Security:** Mitigated by sandboxing the generated HTML/JS in an isolated environment and stripping malicious tags.
