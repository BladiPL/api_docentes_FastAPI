from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int | None = None 
    name: str
    username: str
    user_passw: str