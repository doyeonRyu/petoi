import json

with open("./logs/도연_session.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for msg in data:
    role = msg["type"]
    content = msg["data"]["content"]
    print(f"{role}: {content}")
