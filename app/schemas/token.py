
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None
    refresh_token: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: int | None = None
    rol: str | None = None
