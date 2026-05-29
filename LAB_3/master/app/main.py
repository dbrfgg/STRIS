import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="LAB_3 Master")

STORE: dict[str, Any] = {}
NODE_NAME = os.getenv("NODE_NAME", "master")
REPLICA_URLS = [u.strip() for u in os.getenv("REPLICA_URLS", "").split(",") if u.strip()]


class DataRequest(BaseModel):
    key: str
    value: Any


def replicate_to_one(replica_url: str, payload: dict) -> dict:
    target = f"{replica_url}/replica/data"
    with httpx.Client(timeout=1.5) as client:
        response = client.post(target, json=payload)
    return {"replica": replica_url, "status": "ok", "http_status": response.status_code}


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "node": NODE_NAME}


@app.post("/data")
def write_data(request: DataRequest, mode: str = Query(default="sync")) -> dict:
    STORE[request.key] = request.value
    results = []

    if mode != "sync":
        raise HTTPException(status_code=400, detail="Only mode=sync is supported in this lab")

    for replica_url in REPLICA_URLS:
        try:
            result = replicate_to_one(replica_url, request.model_dump())
            results.append(result)
        except Exception as exc:
            results.append({"replica": replica_url, "status": "error", "error": str(exc)})

    return {
        "node": NODE_NAME,
        "mode": mode,
        "stored": {"key": request.key, "value": request.value},
        "replication": results,
    }


@app.get("/data/{key}")
def read_data(key: str) -> dict:
    return {"node": NODE_NAME, "key": key, "value": STORE.get(key)}


@app.post("/resync")
def resync_all() -> dict:
    # Sends current master state to all replicas after a failure/restart.
    results = []
    for key, value in STORE.items():
        payload = {"key": key, "value": value}
        for replica_url in REPLICA_URLS:
            try:
                result = replicate_to_one(replica_url, payload)
                result["key"] = key
                results.append(result)
            except Exception as exc:
                results.append(
                    {"replica": replica_url, "status": "error", "key": key, "error": str(exc)}
                )
    return {"node": NODE_NAME, "action": "resync", "results": results}
