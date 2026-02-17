from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from lib.auth_service import login_or_create_user, logout_token

router = APIRouter()

class LoginRequest(BaseModel):
    name: str
    contact: str
    user_type: str

@router.post("/login")
def login(req: LoginRequest):
    try:
        return login_or_create_user(
            name=req.name.strip(),
            contact=req.contact.strip(),
            user_type=req.user_type.strip().lower(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
def logout(authorization: str | None = Header(default=None)):
    try:
        logout_token(authorization)
        return {"message": "Logged out"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
