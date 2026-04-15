import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings


class ClinicalTrialsClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.clinical_trials_base_url
        self.timeout = self.settings.request_timeout_seconds

    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
    def fetch_studies(self, params: dict) -> dict:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()

