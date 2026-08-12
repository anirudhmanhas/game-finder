# PlayWeave 🎮

PlayWeave is an intelligent, generative platform that interprets natural language game prompts. It can recommend existing games using semantic vector search or generate completely new, playable HTML5 mini-games on the fly using Google's Gemini LLM.

## Architecture 🏛️

- **Frontend:** React + Vite, styled for a premium, responsive experience.
- **Backend:** Python + FastAPI. Uses `asyncio` to parallelize prompt interpretation and game generation.
- **Database:** PostgreSQL + `pgvector` for semantic similarity searches on existing games.
- **AI Integration:** Google Gemini API (`gemini-flash-lite-latest`) for fast, robust zero-shot code generation and structured intent extraction.
- **Validation:** Headless Chromium (Playwright) sandbox verifies that generated games are syntactically valid and contain a functional HTML5 Canvas.

## Local Development (Native) 💻

### 1. Environment Setup
Create a `.env` file in the project root by copying `.env.example`:
```bash
cp .env.example .env
```
Fill in your `GOOGLE_API_KEY` and the `DATABASE_URL`.

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium
python main.py
```

### 3. Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
The app will be available at `http://localhost:5173`.

## Local Development (Docker) 🐳

For a one-click local setup including the PostgreSQL database:

```bash
docker-compose up --build
```
This spins up the database, the FastAPI backend on `:8000`, and the React frontend on `:5173`.

## Deployment (Render.com) 🚀

PlayWeave is configured for seamless deployment to [Render](https://render.com) using Infrastructure as Code (`render.yaml`).

1. Connect your GitHub repository to Render.
2. Render will automatically detect the `render.yaml` blueprint.
3. It will provision:
   - A free PostgreSQL database (`playweave-db`).
   - A Python FastAPI Web Service (`playweave-backend`).
   - A blazing fast Static Site for the React frontend (`playweave-frontend`).
4. **Important Post-Deploy Step:** Go to the Render Dashboard for your `playweave-backend` service and manually set the `GOOGLE_API_KEY` environment variable. Render blueprints require sensitive keys to be manually provided for security.

## Testing & QA
To run the automated test suite and LLM prompt matrix:
```bash
cd backend
pytest tests/test_regression.py tests/test_qa_matrix.py
```
This ensures prompt understanding and code generation remain robust across 25 diverse edge-cases.
