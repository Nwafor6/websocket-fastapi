from pydantic import BaseModel


class UserSchema(BaseModel):
    id: str | None
    email: str
    password: str
