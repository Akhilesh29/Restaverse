## Restaverse – OAuth‑Protected Real‑Time Web Scraper

This project is a small full‑stack app that demonstrates:

- **Python FastAPI backend** for OAuth 2.0 login, scraping, and cron‑style auto‑fetching.
- **React (Vite) frontend** for a responsive dashboard that only authenticated users can use.
- **Web scraping** with `requests` + `BeautifulSoup`.
- **Optional cron job** (via APScheduler) to refresh data hourly.

The example target site is **Hacker News** (public front page headlines). You can change the scraper to any other public site as needed.

---

### 1. Backend – Setup and OAuth Configuration

#### 1.1. Create and activate virtualenv

```bash
cd Restaverse
py -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
```

#### 1.2. Create OAuth app (GitHub example)

1. Go to GitHub → **Settings → Developer settings → OAuth Apps → New OAuth App**.
2. Use for local dev:
   - **Homepage URL**: `http://localhost:5173`
   - **Authorization callback URL**: `http://localhost:8000/auth/callback`
3. After creating the app, copy:
   - `Client ID`
   - `Client secret`

#### 1.3. Configure environment variables

Create a `.env` file in the project root (`Restaverse/.env`):

```bash
FRONTEND_ORIGIN=http://localhost:5173

OAUTH_CLIENT_ID=YOUR_GITHUB_CLIENT_ID
OAUTH_CLIENT_SECRET=YOUR_GITHUB_CLIENT_SECRET
OAUTH_AUTHORIZE_URL=https://github.com/login/oauth/authorize
OAUTH_TOKEN_URL=https://github.com/login/oauth/access_token
OAUTH_USER_API=https://api.github.com/user
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback

SESSION_SECRET_KEY=some-long-random-secret
```

> The backend uses a lightweight cookie‑based session token (signed with `SESSION_SECRET_KEY`), so the frontend never sees the provider access token – a simple “piggyback” method over OAuth.

#### 1.4. Run the backend

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

#### 2.1. Install and run

```bash
cd Restaverse\frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

#### 2.2. How it works

- On load, the React app calls `GET /auth/me` (with `credentials: 'include'`) to detect an existing session.
- If **not logged in**, it shows a **“Login with OAuth”** button which links to `http://localhost:8000/auth/login`.
- After logging in with GitHub and approving, GitHub redirects back to `http://localhost:8000/auth/callback`, which:
  - Exchanges the code for an access token.
  - Loads your GitHub profile.
  - Creates a signed session token and sets it in an **HttpOnly cookie** (`restaverse_session`).
  - Redirects to the frontend dashboard (`FRONTEND_ORIGIN`).
- The dashboard then shows:
  - **User info** in the header (name + avatar).
  - A **“Fetch Latest Now”** button → `GET /scrape`.
  - A **“Refresh from Cache”** button → `GET /data`.
  - A table of scraped articles (title, link, scrape time).

All protected calls include browser cookies (`credentials: 'include'`).

---

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

You can replace `scrape_hacker_news()` with your own scraper logic (e.g., for a news site, e‑commerce page, etc.).

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

### 5. Deployment (Vercel / Netlify + free backend)

Because Vercel/Netlify don’t run long‑lived Python ASGI servers directly, the recommended deployment is:

- **Backend** (FastAPI):
  - Use a free tier platform such as **Railway**, **Render**, or **Fly.io**.
  - Configure environment variables there (`OAUTH_*`, `SESSION_SECRET_KEY`, `FRONTEND_ORIGIN`).
  - Expose the app on `https://your-backend.example.com`.
- **Frontend** (React + Vite):
  - On **Vercel** or **Netlify**, deploy the `frontend` folder.
  - Set the backend URL in the frontend (change `API_BASE` in `frontend/src/App.tsx` to your deployed backend URL).
  - Update OAuth app callback URL to your backend’s `/auth/callback`.

Example production change in `App.tsx`:

```ts
// const API_BASE = 'http://localhost:8000'
const API_BASE = 'https://your-backend.example.com'
```

And in your remote backend `.env`:

```bash
FRONTEND_ORIGIN=https://your-frontend.vercel.app
```

---

### 6. Example Workflow (End‑to‑End)

1. **Start services locally**
   - Backend: `uvicorn backend.app:app --reload --port 8000`
   - Frontend: `npm run dev` inside `frontend`.
2. **Login with OAuth**
   - Open `http://localhost:5173`.
   - Click **“Login with OAuth”** (GitHub).
   - Authorize the app and let it redirect back to the dashboard.
3. **Trigger real‑time scraping**
   - Click **“Fetch Latest Now”**.
   - Watch the table populate with scraped items.
4. **Automatic hourly refresh**
   - Leave the backend running; APScheduler will refresh the data about every hour.
   - Use **“Refresh from Cache”** to see the most recently stored dataset.

This satisfies the assignment requirements: OAuth integration, authenticated access to scraping, web scraping with Python, real‑time fetch, optional cron job, clean UI/UX, and documentation plus deployment guidance.


# Restaverse
