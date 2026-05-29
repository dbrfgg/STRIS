import os
import random
import string
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from redis import Redis
from redis.exceptions import RedisError

app = Flask(__name__)

SERVICE_NAME = os.getenv("SERVICE_NAME", "service-unknown")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def generate_value(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


@app.get("/info")
def info():
    now = datetime.now(timezone.utc).isoformat()
    return jsonify({"service": SERVICE_NAME, "time": now})


@app.get("/data")
def data():
    raw_id = request.args.get("id")
    if raw_id is None:
        return jsonify({"error": "Query parameter 'id' is required"}), 400

    try:
        data_id = int(raw_id)
    except ValueError:
        return jsonify({"error": "Query parameter 'id' must be an integer"}), 400

    key = f"data:{data_id}"

    try:
        cached = redis_client.get(key)
        if cached is not None:
            return jsonify({"id": data_id, "value": cached, "source": "cache"})

        generated = generate_value()
        redis_client.set(key, generated)
        return jsonify({"id": data_id, "value": generated, "source": "generated"})
    except RedisError:
        return jsonify({"error": "Cache is temporarily unavailable"}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
