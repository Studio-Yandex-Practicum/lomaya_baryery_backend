from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from src.core.db.models import Shift


class ShiftDB(BaseModel):
    id: int
    status: Shift.Status
    created_date: Optional[datetime] = Field(datetime.now())
    updated_date: Optional[datetime] = Field(datetime.now())

    class Config:
        orm_mode = True
