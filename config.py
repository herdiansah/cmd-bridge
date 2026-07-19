"""Local, untracked bridge configuration."""

from pathlib import Path

ENV_PATH = Path(__file__).with_name(".env")


def load_config() -> dict[str, str]:
    if not ENV_PATH.is_file():
        raise SystemExit(f"Configuration file not found: {ENV_PATH}. Copy .env.example to .env.")

    config: dict[str, str] = {}
    for number, line in enumerate(ENV_PATH.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise SystemExit(f"Invalid .env line {number}: expected KEY=VALUE")
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit(f"Invalid .env line {number}: empty key")
        config[key] = value.strip().strip('"').strip("'")
    return config
