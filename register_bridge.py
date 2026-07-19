import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from config import load_config

DB_PATH = os.path.join(os.environ["APPDATA"], "9router", "db", "data.sqlite")
NODE_NAME = "CommandCode Bridge"
PREFIX = "cmdcode"
BASE_URL = "http://127.0.0.1:8320/v1"
CONFIG = load_config()


def register() -> None:
    if not os.path.exists(DB_PATH):
        raise SystemExit(f"9router database not found: {DB_PATH}")

    api_key = CONFIG.get("COMMAND_CODE_API_KEY")
    if not api_key:
        raise SystemExit("COMMAND_CODE_API_KEY is required")

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    node_id = "openai-compatible-chat-" + str(uuid.uuid4())
    node_data = {"prefix": PREFIX, "apiType": "chat", "baseUrl": BASE_URL}
    connection_data = {
        "defaultModel": "cmdcode/deepseek/deepseek-v4-pro",
        "apiKey": api_key,
        "testStatus": "active",
        "providerSpecificData": {
            **node_data,
            "nodeName": NODE_NAME,
            "connectionProxyEnabled": False,
            "connectionProxyUrl": "",
            "connectionNoProxy": "",
        },
    }

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kv WHERE scope = 'customModels' AND key LIKE '%|cmdcode/%|llm'")
        cursor.execute(
            "SELECT id FROM providerNodes WHERE json_extract(data, '$.prefix') IN (?, ?)",
            (PREFIX, "commandcode"),
        )
        old_node_ids = [row[0] for row in cursor.fetchall()]
        for old_node_id in old_node_ids:
            cursor.execute("DELETE FROM providerConnections WHERE provider = ?", (old_node_id,))
            cursor.execute("DELETE FROM kv WHERE scope = 'customModels' AND key LIKE ?", (f"{old_node_id}|%",))
            cursor.execute("DELETE FROM providerNodes WHERE id = ?", (old_node_id,))

        cursor.execute(
            "INSERT INTO providerNodes (id, type, name, data, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?, ?)",
            (node_id, "openai-compatible", NODE_NAME, json.dumps(node_data), now, now),
        )
        cursor.execute(
            "INSERT INTO providerConnections (id, provider, authType, name, priority, isActive, data, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                node_id,
                "apikey",
                "CommandCode",
                1,
                1,
                json.dumps(connection_data),
                now,
                now,
            ),
        )

    print(f"Registered {NODE_NAME} as {PREFIX}/… in 9router.")


if __name__ == "__main__":
    register()
