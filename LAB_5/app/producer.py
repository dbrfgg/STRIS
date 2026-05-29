import json
from kafka import KafkaProducer

TOPIC = "transactions"

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    key_serializer=lambda k: str(k).encode("utf-8"),
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
)

messages = [
    {"user_id": 101, "amount": 120.5, "type": "incoming"},
    {"user_id": 101, "amount": 30.0, "type": "outgoing"},
    {"user_id": 202, "amount": 500.0, "type": "incoming"},
    {"user_id": 303, "amount": 88.0, "type": "outgoing"},
    {"user_id": 202, "amount": 10.0, "type": "outgoing"},
    {"user_id": 101, "amount": 5.0, "type": "outgoing"},
    {"user_id": 303, "amount": 72.0, "type": "incoming"},
    {"user_id": 404, "amount": 900.0, "type": "incoming"},
    {"user_id": 404, "amount": 250.0, "type": "outgoing"},
    {"user_id": 202, "amount": 15.0, "type": "incoming"},
]

for item in messages:
    fut = producer.send(TOPIC, key=item["user_id"], value=item)
    meta = fut.get(timeout=10)
    print(
        f"sent user_id={item['user_id']} partition={meta.partition} offset={meta.offset} payload={item}"
    )

producer.flush()
print("All messages sent")
