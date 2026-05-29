import json
from kafka import KafkaConsumer

TOPIC = "transactions"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers="kafka:9092",
    group_id="transaction-group",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    key_deserializer=lambda k: k.decode("utf-8") if k else None,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

print("Consumer started (group=transaction-group)")
for msg in consumer:
    print(
        f"partition={msg.partition} offset={msg.offset} key={msg.key} value={msg.value}"
    )
