"""Polls foundation services' health endpoints before the smoke test runs."""
import sys
import time

import httpx

CHECKS = [
    ("db-tool", "http://localhost:8101/health"),
    ("email-tool", "http://localhost:8102/health"),
    ("file-tool", "http://localhost:8103/health"),
    ("mailhog", "http://localhost:8025/api/v2/messages"),
    ("agent", "http://localhost:8000/health"),
]

TIMEOUT_S = 120
INTERVAL_S = 2


def wait_for(name: str, url: str, deadline: float) -> bool:
    while time.time() < deadline:
        try:
            resp = httpx.get(url, timeout=3.0)
            if resp.status_code < 500:
                print(f"[ok] {name}")
                return True
        except Exception:
            pass
        time.sleep(INTERVAL_S)
    print(f"[FAIL] {name} did not become healthy in time")
    return False


def main() -> int:
    deadline = time.time() + TIMEOUT_S
    ok = True
    for name, url in CHECKS:
        ok = wait_for(name, url, deadline) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
