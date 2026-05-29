import os
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="LAB_2 Replica Node")

STORE: dict[str, Any] = {}
NODE_NAME = os.getenv("NODE_NAME", "replica")


class SetRequest(BaseModel):
    key: str
    value: Any


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "node": NODE_NAME}


@app.post("/replicate/set")
def replicate_set(request: SetRequest) -> dict:
    STORE[request.key] = request.value
    return {
        "status": "replicated",
        "node": NODE_NAME,
        "key": request.key,
        "value": request.value,
    }


@app.get("/replicate/get/{key}")
def replicate_get(key: str) -> dict:
    return {
        "status": "ok",
        "node": NODE_NAME,
        "key": key,
        "value": STORE.get(key),
    }


@app.get("/state")
def state() -> dict:
    return {"node": NODE_NAME, "store": STORE}
