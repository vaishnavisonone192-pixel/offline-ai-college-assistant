import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


class OllamaServiceError(RuntimeError):
    pass


def generate_response(prompt: str) -> str:
    """Generate a response using the locally running Ollama model."""
    payload = json.dumps(
        {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    ).encode("utf-8")
    request = Request(
        f"{OLLAMA_URL.rstrip('/')}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise OllamaServiceError(
            "Ollama is unavailable. Start Ollama and make sure "
            f"the {OLLAMA_MODEL} model is installed."
        ) from error

    answer = result.get("response", "").strip()
    if not answer:
        raise OllamaServiceError("Ollama returned an empty response.")
    return answer
