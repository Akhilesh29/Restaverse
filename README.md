## Restaverse – OAuth‑Protected Real‑Time Web Scraper

This project is a small full‑stack app that demonstrates:

- **Python FastAPI backend** for OAuth 2.0 login, scraping, and cron‑style auto‑fetching.
- **React (Vite) frontend** for a responsive dashboard that only authenticated users can use.
- **Web scraping** with `requests` + `BeautifulSoup`.
- **Optional cron job** (via APScheduler) to refresh data hourly.


---

### 1. Backend – Setup

#### 1.1. Create and activate virtualenv

```bash
cd Restaverse
py -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
```

#### 1.2 Run the backend

```bash
.venv\Scripts\activate
uvicorn backend.app:app --reload --port 8000
```

Backend endpoints (partial):

- `GET /ping` – health check.
- `GET /auth/login` – starts OAuth flow (redirect to GitHub).
- `GET /auth/callback` – GitHub redirects here; backend creates an app session cookie.
- `GET /auth/me` – returns current user info (requires session cookie).
- `GET /scrape` – triggers real‑time scraping (requires auth).
- `GET /data` – returns latest scraped data from cache/JSON (requires auth).

The scraper logic is in `backend/scraper.py` and currently targets `https://news.ycombinator.com/`.

---

### 2. Frontend – React Dashboard

#### Install and run

```bash
cd Restaverse\frontend
npm install
npm run dev
```


### 3. Web Scraping & Data Storage

- Implemented in `backend/scraper.py` using:
  - `requests` for HTTP requests.
  - `BeautifulSoup` for HTML parsing.
- Current example:
  - Scrapes Hacker News front page rows with CSS selector `tr.athing`.
  - Extracts `title`, `url`, and a timestamp.
- Data is stored:
  - In memory (simple Python list cache).
  - In `backend/data/latest_articles.json` on disk.


---

### 4. Real‑Time Fetching & Cron‑Style Auto‑Fetch

#### 4.1. Real‑time fetching

- Frontend’s **“Fetch Latest Now”** button calls:

  - `GET /scrape` → triggers a live scrape and returns fresh results.

- UI updates immediately (loading state + error handling).

#### 4.2. Automated fetching with cron (APScheduler)

- In `backend/app.py`:
  - On startup, the app:
    - Attempts an initial scrape.
    - Starts an **APScheduler background job**:

      - `scrape_hacker_news` runs every **60 minutes**.

- The frontend can call `GET /data` at any time to read the most recent dataset produced by either manual or scheduled scrapes.

> For production, consider moving to a dedicated scheduler (e.g., a cloud cron or separate worker) instead of in‑process APScheduler.

---

### 5. Deployment (Vercel / Netlify )

Vercel/Netlify don’t run long‑lived Python ASGI servers directly.




