import os
import httpx
import jwt
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from dotenv import load_dotenv

router = APIRouter(prefix="/auth", tags=["auth"])

# Environment variables
load_dotenv()
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "your_client_id")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "your_client_secret")
JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_key")
JWT_ALGORITHM = "HS256"

@router.get("/github/login")
def github_login():
    """Redirects the user to GitHub's OAuth login page."""
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}&redirect_uri=http://localhost:8000/auth/github/callback"
    )
    return RedirectResponse(github_auth_url)

@router.get("/github/callback")
async def github_callback(code: str, db: Session = Depends(get_db)):
    """Handles GitHub's redirect, exchanges code for token, and issues a JWT."""
    # 1. Exchange code for access token
    token_url = "https://github.com/login/oauth/access_token"
    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
    }
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, json=payload, headers=headers)
        data = response.json()
        access_token = data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token from GitHub")

        # 2. Fetch user profile from GitHub
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
        )
        github_user = user_resp.json()

    github_id = github_user.get("id")
    login = github_user.get("login")

    if not github_id or not login:
        raise HTTPException(status_code=400, detail="Could not retrieve user info from GitHub")

    # 3. Upsert user in database
    user = db.query(User).filter(User.github_id == github_id).first()
    if not user:
        user = User(github_id=github_id, username=login)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update username if user changed it on GitHub
        if user.username != login:
            user.username = login
            db.commit()
            db.refresh(user)

    # 4. Issue JWT token using database user's id
    jwt_token = jwt.encode({"sub": user.id, "login": login}, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # 5. Redirect back to frontend with the token in query params (or handle via cookie)
    return RedirectResponse(f"http://localhost:5173?token={jwt_token}")
