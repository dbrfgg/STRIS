import os
import time
from datetime import datetime, timezone
from threading import Thread

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://lab7:lab7@postgres:5432/lab7")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="created")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Outbox(Base):
    __tablename__ = "outbox"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    aggregate_type: Mapped[str] = mapped_column(String(64), nullable=False)
    aggregate_id: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[str] = mapped_column(String(2048), nullable=False)
    sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PublishedMessage(Base):
    __tablename__ = "published_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    outbox_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    topic: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[str] = mapped_column(String(2048), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CreateOrderRequest(BaseModel):
    user_id: int
    amount: float


app = FastAPI(title="LAB_7 Transactional Outbox")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)

    def relay_loop() -> None:
        while True:
            try:
                with SessionLocal() as db:
                    events = (
                        db.query(Outbox)
                        .filter(Outbox.sent.is_(False))
                        .order_by(Outbox.id.asc())
                        .limit(20)
                        .all()
                    )
                    for event in events:
                        # Idempotency: unique outbox_id in published_messages avoids duplicate publish.
                        already = (
                            db.query(PublishedMessage)
                            .filter(PublishedMessage.outbox_id == event.id)
                            .first()
                        )
                        if already:
                            event.sent = True
                            continue

                        db.add(
                            PublishedMessage(
                                outbox_id=event.id,
                                topic="orders.created",
                                payload=event.payload,
                                published_at=datetime.now(timezone.utc),
                            )
                        )
                        event.sent = True

                    db.commit()
            except Exception:
                pass

            time.sleep(1.0)

    Thread(target=relay_loop, daemon=True).start()


@app.get("/health")
def health() -> dict:
    with engine.connect() as conn:
        conn.execute(text("select 1"))
    return {"status": "ok"}


@app.post("/orders")
def create_order(payload: CreateOrderRequest) -> dict:
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        try:
            order = Order(
                user_id=payload.user_id,
                amount=payload.amount,
                status="created",
                created_at=now,
            )
            db.add(order)
            db.flush()

            event_payload = (
                f'{{"order_id": {order.id}, "user_id": {payload.user_id}, '
                f'"amount": {payload.amount}, "event": "order_created"}}'
            )
            db.add(
                Outbox(
                    aggregate_type="order",
                    aggregate_id=order.id,
                    event_type="order_created",
                    payload=event_payload,
                    sent=False,
                    created_at=now,
                )
            )

            db.commit()
            return {"order_id": order.id, "status": "created"}
        except Exception as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"transaction failed: {exc}")


@app.get("/debug/state")
def debug_state() -> dict:
    with SessionLocal() as db:
        orders = db.query(Order).order_by(Order.id.asc()).all()
        outbox = db.query(Outbox).order_by(Outbox.id.asc()).all()
        published = db.query(PublishedMessage).order_by(PublishedMessage.id.asc()).all()

        return {
            "orders": [
                {
                    "id": o.id,
                    "user_id": o.user_id,
                    "amount": float(o.amount),
                    "status": o.status,
                }
                for o in orders
            ],
            "outbox": [
                {
                    "id": e.id,
                    "aggregate_id": e.aggregate_id,
                    "event_type": e.event_type,
                    "sent": e.sent,
                }
                for e in outbox
            ],
            "published_messages": [
                {
                    "id": p.id,
                    "outbox_id": p.outbox_id,
                    "topic": p.topic,
                    "payload": p.payload,
                }
                for p in published
            ],
        }
