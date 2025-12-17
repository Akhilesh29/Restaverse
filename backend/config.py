import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Basic app config
    APP_NAME: str = "Restaverse Scraper API"
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    # OAuth config (example: GitHub)
    OAUTH_CLIENT_ID: str = os.getenv("OAUTH_CLIENT_ID", "")
    OAUTH_CLIENT_SECRET: str = os.getenv("OAUTH_CLIENT_SECRET", "")
    OAUTH_AUTHORIZE_URL: str = os.getenv(
        "OAUTH_AUTHORIZE_URL", "https://github.com/login/oauth/authorize"
    )
    OAUTH_TOKEN_URL: str = os.getenv(
        "OAUTH_TOKEN_URL", "https://github.com/login/oauth/access_token"
    )
    OAUTH_USER_API: str = os.getenv(
        "OAUTH_USER_API", "https://api.github.com/user"
    )
    OAUTH_REDIRECT_URI: str = os.getenv(
        "OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback"
    )

    # Session / JWT secret (for lightweight session token - "pig method")
    SESSION_SECRET_KEY: str = os.getenv(
        "SESSION_SECRET_KEY", "change-this-session-secret"
    )


settings = Settings()


