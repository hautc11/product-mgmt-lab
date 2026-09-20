import time

import httpx

BASE_URL = "http://localhost:8000"
LIMIT = 20
REPEAT = 5

def timed_get(path):
    times = []
    data = None
    for _ in range(REPEAT):
        start = time.perf_counter()
        response = httpx.get(f"{BASE_URL}{path}")
        response.raise_for_status()
        times.append(time.perf_counter() - start)
        data = response.json()
    avg_ms = (sum(times) / len(times)) * 1000
    return data, avg_ms

def main():
    # Warm-up
    httpx.get(f"{BASE_URL}/products?limit=1")

    # Offset
    first_page, t = timed_get(f"/products?skip=0&limit={LIMIT}")
    total = first_page["total"]
    print(f"[offset] first page (skip=0): {t:.2f}ms (avg of {REPEAT})")

    deep_skip = max(total - LIMIT, 0)
    deep_page, t = timed_get(f"/products?skip={deep_skip}&limit={LIMIT}")
    print(f"[offset] deep-est page (skip={deep_skip}): {t:.2f}ms (avg of {REPEAT})")

    # Cursor
    _, t = timed_get(f"/products?cursor&limit={LIMIT}")
    print(f"[cursor] first page (cursor=None): {t:.2f}ms (avg of {REPEAT})")

    near_end_cursor = deep_page["items"][0]["id"] - 1
    _, t = timed_get(f"/products?cursor={near_end_cursor}&limit={LIMIT}")
    print(f"[cursor] deep-est page (cursor={near_end_cursor}): {t:.2f}ms (avg of {REPEAT})")


if __name__ == "__main__":
    main()