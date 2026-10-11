from datetime import datetime

from sqlalchemy import DateTime, String, false, func
from sqlalchemy.orm import Mapped, mapped_column

from blasto.models.base import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(
        String(320)
    )  # 320 = maximum length of an email address
    training_type: Mapped[str] = mapped_column(String(20))  # "online" or "in_person"
    cat_a: Mapped[bool] = mapped_column(server_default=false())
    cat_am: Mapped[bool] = mapped_column(server_default=false())
    cat_b: Mapped[bool] = mapped_column(server_default=false())
    cat_be: Mapped[bool] = mapped_column(server_default=false())
    cat_c: Mapped[bool] = mapped_column(server_default=false())
    cat_ce: Mapped[bool] = mapped_column(server_default=false())
    cat_d: Mapped[bool] = mapped_column(server_default=false())
    cat_95: Mapped[bool] = mapped_column(server_default=false())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Postgres fills in the time on insert
    )
