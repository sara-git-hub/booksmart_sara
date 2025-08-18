# Copilot Instructions for BookSmart

## Project Overview
BookSmart is a full-stack application for library management and book recommendation. It uses FastAPI for the backend, Jinja2 for templating, SQLAlchemy for ORM, and Tailwind CSS for frontend styling. The project is organized into clear service boundaries: backend (API, business logic, models), frontend (templates, static assets), and data (CSV sources).

## Architecture & Key Components
- **Backend** (`backend/`):
  - `main.py`: FastAPI app entrypoint, includes all routers and session middleware.
  - `routes/`: API endpoints grouped by domain (admin, users, livres, reservations, recommandations, stats).
  - `models.py`, `schemas.py`: SQLAlchemy models and Pydantic schemas for DB structure and API validation.
  - `crud.py`: Data access logic, e.g., user authentication, book queries.
  - `recommender/`: TF-IDF and cosine similarity model for book recommendations (see `recommender.py`).
  - `scraping/`: Selenium-based book scraping script.
  - `config.py`: Centralized config, including Jinja2 template setup.
- **Frontend** (`frontend/`):
  - `templates/`: Jinja2 HTML templates, organized by page and admin section.
  - `static/`: CSS (Tailwind), JS (Chart.js, main.js), images.
- **Data** (`data/`):
  - CSV files for raw and cleaned book data.

## Developer Workflows
- **Run locally:**
  - Use `run.sh` (Linux/macOS) or `uvicorn backend.main:app --reload` (Windows) to start the FastAPI server.
- **Database:**
  - Tables are auto-created on startup via SQLAlchemy's `Base.metadata.create_all`.
- **Testing:**
  - Tests are in `tests/` (e.g., `test_auth.py`). Use `pytest` for running tests.
- **Scraping & Model Training:**
  - Run `scraping/scrap_books_toscrape.py` to fetch book data.
  - Run `recommender/recommender.py` to train and save TF-IDF and similarity models.

## Project-Specific Patterns
- **Routing:**
  - All API routes are prefixed (`/api` for user, book, stats, recommendations; `/admin` for admin).
- **Templates:**
  - All pages extend `base.html` for layout consistency.
  - Admin templates are in `templates/admin/`.
- **Session & Auth:**
  - User session is managed via FastAPI's `SessionMiddleware`.
  - Auth logic is in `crud.py` and `routes/users.py`.
- **Recommendation:**
  - Uses precomputed TF-IDF and cosine similarity matrices loaded via `joblib`.
- **Forms:**
  - Jinja2 forms POST to API endpoints; backend expects `Form(...)` for input parsing.

## Integration Points
- **External:**
  - Selenium (scraping), scikit-learn (TF-IDF, similarity), passlib (password hashing).
- **Internal:**
  - Cross-component communication via SQLAlchemy models and FastAPI dependency injection.

## Examples
- To add a new admin page, create a route in `routes/admin.py` and a template in `templates/admin/`.
- To extend book recommendation, update `recommender/recommender.py` and reload models in `routes/recommandations.py`.

---
For unclear or missing conventions, please provide feedback so this guide can be improved.
