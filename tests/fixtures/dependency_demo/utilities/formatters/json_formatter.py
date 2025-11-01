import json


def serialize(message: str) -> str:
    return json.dumps({"message": message})
