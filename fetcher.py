import random
import time

import requests

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def retry_request(
        method: str,
        url: str,
        max_retries: int = 5,
        backoff_base: float = 0.5,
        backoff_max: float = 10,
        retry_statuses=RETRYABLE_STATUS_CODES,
        **kwargs: dict[str, any],
):
    for attempt in range(max_retries):
        try:
            response = requests.request(
                method,
                url,
                headers={"User-Agent": USER_AGENT},
                **kwargs,
            )
            if response.status_code not in retry_statuses:
                return response
            else:
                raise requests.HTTPError(f"Retryable HTTP error: {response.status_code}", response=response)
        except (requests.RequestException, requests.HTTPError) as e:
            if attempt == max_retries - 1:
                raise
            sleep_time = min(backoff_max, backoff_base * (2 ** attempt))
            jitter = random.uniform(0, sleep_time)
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {jitter:.2f}s...")
            time.sleep(jitter)
