# PlayWeave 🎮 (Made by Boiler_Plate_Dine)

PlayWeave is an intelligent, generative platform that interprets natural language game prompts. It can recommend existing games using semantic vector search with real-time AI-generated popularity metrics, or generate completely new, playable HTML5 mini-games on the fly using Google's Gemini LLM.

## Features ✨
- **Natural Language Parsing:** Interprets complex user requests (e.g., "A relaxing 2D puzzle game").
- **Smart Recommendations:** Uses `pgvector` for semantic similarity searches on a database of existing games.
- **Dynamic AI Popularity:** Dynamically injects AI-generated popularity scores and rationale for each recommended game.
- **Generative AI Mini-Games:** Asks for confirmation before generating custom, playable HTML5 Canvas mini-games directly in your browser.
- **Minimalist UI:** Clean, modern, information-dense interface without unnecessary image clutter.

## Architecture 🏛️

- **Frontend:** React + Vite, styled for a premium, responsive experience.
- **Backend:** Python + FastAPI. Uses `asyncio` to parallelize prompt interpretation and game generation.
- **Database:** PostgreSQL + `pgvector` for semantic similarity searches on existing games.
- **AI Integration:** Google Gemini API (`gemini-flash-lite-latest`) for fast, robust zero-shot code generation and structured intent extraction.
- **Validation:** Headless Chromium (Playwright) sandbox verifies that generated games are syntactically valid and contain a functional HTML5 Canvas.

## Local Development (Docker) 🐳

For a one-click local setup including the PostgreSQL database:

```bash
docker-compose up --build -d
```
This spins up the database, the FastAPI backend on `:8000`, and the React frontend on `:5173`.

## Deployment (Render.com) 🚀

PlayWeave is configured for seamless deployment to [Render](https://render.com) using Infrastructure as Code (`render.yaml`).

1. Connect your GitHub repository to Render and create a new **Blueprint**.
2. Render will automatically provision:
   - A free PostgreSQL database (`playweave-db`).
   - A Python FastAPI Web Service (`playweave-backend`).
   - A blazing fast Static Site for the React frontend (`playweave-frontend`).
3. **Important Post-Deploy Step:** Go to the Render Dashboard for your `playweave-backend` service and manually set the `GOOGLE_API_KEY` environment variable.
4. **Database Seeding:** Because Render's free tier disables shell access, you must seed the production database via the web. Once the backend is live, navigate to `https://<YOUR_BACKEND_URL>.onrender.com/seed` in your browser. This will instantly populate the cloud database with 200 sample games for the search engine.

## Testing & QA
To run the automated test suite and LLM prompt matrix:
```bash
cd backend
pytest tests/test_regression.py tests/test_qa_matrix.py
```
This ensures prompt understanding and code generation remain robust across 25 diverse edge-cases.
