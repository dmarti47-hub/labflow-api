from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr


UserRole = Literal["admin", "tech"]


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    role: UserRole
