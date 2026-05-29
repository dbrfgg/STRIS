import os
from typing import Any

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="LAB_2 Master Node")

STORE: dict[str, Any] = {}
REPLICA_URLS = [u.strip() for u in os.getenv("REPLICA_URLS", "").split(",") if u.strip()]
NODE_NAME = os.getenv("NODE_NAME", "master")


class SetRequest(BaseModel):
    key: str
    value: Any


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "node": NODE_NAME}


@app.post("/set")
def set_value(request: SetRequest) -> dict:
    STORE[request.key] = request.value
    replication_results = []

    for replica_url in REPLICA_URLS:
        target = f"{replica_url}/replicate/set"
        try:
            with httpx.Client(timeout=1.5) as client:
                response = client.post(target, json=request.model_dump())
            replication_results.append(
                {
                    "replica": replica_url,
                    "status": "ok",
                    "http_status": response.status_code,
                }
            )
        except Exception as exc:
            replication_results.append(
                {"replica": replica_url, "status": "error", "error": str(exc)}
            )

    return {
        "node": NODE_NAME,
        "action": "set",
        "key": request.key,
        "value": request.value,
        "replication": replication_results,
    }


@app.get("/get/{key}")
def get_value(key: str) -> dict:
    local_value = STORE.get(key)
    replica_reads = []

    for replica_url in REPLICA_URLS:
        target = f"{replica_url}/replicate/get/{key}"
        try:
            with httpx.Client(timeout=1.5) as client:
                response = client.get(target)
            replica_reads.append(
                {
                    "replica": replica_url,
                    "status": "ok",
                    "http_status": response.status_code,
                    "body": response.json(),
                }
            )
        except Exception as exc:
            replica_reads.append(
                {"replica": replica_url, "status": "error", "error": str(exc)}
            )

    return {
        "node": NODE_NAME,
        "action": "get",
        "key": key,
        "local_value": local_value,
        "replica_reads": replica_reads,
    }


@app.get("/state")
def state() -> dict:
    return {"node": NODE_NAME, "store": STORE}
