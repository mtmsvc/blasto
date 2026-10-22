from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreate(BaseModel):  # the request body of POST /applications
    name: str = Field(max_length=200)  # same limits as the database columns
    phone: str = Field(max_length=50)
    email: str = Field(max_length=320)
    training_type: Literal["online", "in_person"]  # any other value → 422 error
    cat_a: bool = False  # categories are optional; missing = False
    cat_am: bool = False
    cat_b: bool = False
    cat_be: bool = False
    cat_c: bool = False
    cat_ce: bool = False
    cat_d: bool = False
    cat_95: bool = False


class ApplicationPublic(ApplicationCreate):
    model_config = ConfigDict(
        from_attributes=True
    )  # lets Pydantic read a SQLAlchemy object's attributes

    id: int
    created_at: datetime
