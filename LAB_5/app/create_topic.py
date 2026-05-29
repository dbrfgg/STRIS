import json
from kafka.admin import KafkaAdminClient, NewTopic

TOPIC = "transactions"

admin = KafkaAdminClient(bootstrap_servers="kafka:9092", client_id="lab5-admin")
existing = admin.list_topics()
if TOPIC not in existing:
    admin.create_topics([
        NewTopic(name=TOPIC, num_partitions=3, replication_factor=1)
    ])
    print(f"Created topic: {TOPIC}")
else:
    print(f"Topic already exists: {TOPIC}")

print("Done")
