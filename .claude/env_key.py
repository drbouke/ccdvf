"""Print the course API key from .env for the apiKeyHelper setting."""
from pathlib import Path

env_file = Path(__file__).parent.parent / ".env"
for line in env_file.read_text(encoding="utf-8").splitlines():
    if line.startswith("ANTHROPIC_API_KEY="):
        print(line.split("=", 1)[1].strip())
