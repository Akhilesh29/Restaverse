from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apscheduler.schedulers.background import BackgroundScheduler

from .config import settings
from .auth import router as auth_router, get_current_user
from .scraper import scrape_hacker_news, get_latest


app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.get("/scrape")
def scrape_now(user=Depends(get_current_user)):
    """
    Trigger a real-time scrape. Protected by auth.
    """
    items = scrape_hacker_news()
    return {"source": "live", "count": len(items), "items": items}


@app.get("/data")
def data(user=Depends(get_current_user)):
    """
    Get the latest scraped data (from cache/JSON).
    """
    return get_latest()


_scheduler: BackgroundScheduler | None = None


def _start_scheduler() -> None:
    global _scheduler
    if _scheduler:
        return
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        scrape_hacker_news,
        "interval",
        minutes=60,
        id="scrape_hn_job",
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler


@app.on_event("startup")
def on_startup():
    # Warm cache and start cron-style job
    try:
        scrape_hacker_news()
    except Exception:
        # Don't block startup if the first scrape fails
        pass
    _start_scheduler()


@app.exception_handler(Exception)
async def global_exception_handler(_, exc: Exception):
    # Simple global error handler for nicer responses
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc) or "Internal server error"},
    )



