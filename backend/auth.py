from typing import Optional, Dict, Any
import secrets
import requests
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse

from itsdangerous import TimestampSigner, BadSignature, SignatureExpired

from .config import settings


router = APIRouter(prefix="/auth", tags=["auth"])

signer = TimestampSigner(settings.SESSION_SECRET_KEY)

# In-memory map of session_id -> user profile (very lightweight "pig" method)
_sessions: Dict[str, Dict[str, Any]] = {}


def _create_session(user: Dict[str, Any]) -> str:
    session_id = secrets.token_urlsafe(32)
    _sessions[session_id] = user
    token = signer.sign(session_id).decode("utf-8")
    return token


def _read_session(token: str, max_age: int = 60 * 60 * 8) -> Optional[Dict[str, Any]]:
    try:
        session_id = signer.unsign(token, max_age=max_age).decode("utf-8")
    except (BadSignature, SignatureExpired):
        return None
    return _sessions.get(session_id)


def get_current_user(request: Request) -> Dict[str, Any]:
    token = request.cookies.get("restaverse_session")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    user = _read_session(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )
    return user


@router.get("/login")
def login() -> RedirectResponse:
    """
    Start OAuth flow. Frontend simply opens this URL.
    Uses a lightweight server-side session token - the frontend never
    sees provider tokens (a common \"piggyback\" style approach).
    """
    if not settings.OAUTH_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="OAuth is not configured. Set OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET.",
        )

    params = {
        "client_id": settings.OAUTH_CLIENT_ID,
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
        "scope": "read:user",
        "response_type": "code",
    }
    from urllib.parse import urlencode

    url = f"{settings.OAUTH_AUTHORIZE_URL}?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/callback")
def callback(code: str, response: Response) -> RedirectResponse:
    """
    Exchange authorization code for an access token and create app session.
    """
    if not settings.OAUTH_CLIENT_ID or not settings.OAUTH_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="OAuth is not configured. Set OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET.",
        )

    data = {
        "client_id": settings.OAUTH_CLIENT_ID,
        "client_secret": settings.OAUTH_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
    }
    headers = {"Accept": "application/json"}
    token_resp = requests.post(
        settings.OAUTH_TOKEN_URL, data=data, headers=headers, timeout=10
    )
    if token_resp.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange code: {token_resp.text}",
        )
    token_json = token_resp.json()
    access_token = token_json.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=400,
            detail="No access token in OAuth response",
        )

    # Get user profile
    user_resp = requests.get(
        settings.OAUTH_USER_API,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if user_resp.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to load user profile: {user_resp.text}",
        )
    user = user_resp.json()

    session_token = _create_session(
        {
            "id": user.get("id"),
            "name": user.get("name") or user.get("login"),
            "login": user.get("login"),
            "avatar_url": user.get("avatar_url"),
        }
    )

    response = RedirectResponse(url=f"{settings.FRONTEND_ORIGIN}/")
    # HttpOnly cookie so frontend JS can't read it, just piggybacks on browser
    response.set_cookie(
        "restaverse_session",
        session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 8,
    )
    return response


@router.post("/logout")
def logout(response: Response) -> Dict[str, str]:
    response.delete_cookie("restaverse_session")
    return {"message": "Logged out"}


@router.get("/me")
def me(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    return current_user


