import os
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="LAB_3 Replica")

STORE: dict[str, Any] = {}
NODE_NAME = os.getenv("NODE_NAME", "replica")


class DataRequest(BaseModel):
    key: str
    value: Any


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "node": NODE_NAME}


@app.post("/replica/data")
def replicate_data(request: DataRequest) -> dict:
    STORE[request.key] = request.value
    return {
        "status": "replicated",
        "node": NODE_NAME,
        "key": request.key,
        "value": request.value,
    }


@app.get("/data/{key}")
def read_data(key: str) -> dict:
    return {"node": NODE_NAME, "key": key, "value": STORE.get(key)}
