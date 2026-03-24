import os
import time
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class CHESClient:
    # How many seconds before expiry to proactively refresh the token
    _TOKEN_REFRESH_BUFFER = 30

    def __init__(self, check_health: bool = True):
        """
        Initialize the client.

        Reads the following from the environment:
            CHES_API_URL        - Base URL for the CHES API
            CHES_LOGIN_URL      - LoginProxy token endpoint
            CHES_CLIENT_ID      - OAuth2 client ID
            CHES_CLIENT_SECRET  - OAuth2 client secret
            CHES_FROM           - Sender address
            CHES_TO             - Recipient address
            CHES_SUBJECT_PREFIX - Subject prefix (e.g. "[BCWAT DEV - Airflow]")
        """
        self._api_url = os.environ.get("CHES_API_URL")
        self._login_url = os.environ.get("CHES_LOGIN_URL")
        self._client_id = os.environ.get("CHES_CLIENT_ID")
        self._client_secret = os.environ.get("CHES_CLIENT_SECRET")
        self._from_address = os.environ.get("CHES_FROM")
        self._to_address = os.environ.get("CHES_TO")
        self._subject_prefix = os.environ.get("CHES_SUBJECT_PREFIX", "")

        # Token cache
        self._access_token: str | None = None
        self._token_expires_at: float = 0.0  # unix timestamp

        if check_health:
            self.health_check()

    def health_check(self):
        """
        GET /health — checks CHES and its external dependencies.
        """
        url = f"{self._api_url}/health"
        response = requests.get(url, headers=self._auth_headers(), timeout=10)

        if response.status_code != 200:
            raise Exception(
                f"CHES health check failed: HTTP {response.status_code} — {response.text}"
            )

        data = response.json()
        print(f"[CHES] Health check passed: {data}")
        return data

    def send_email(self, subject: str, body: str):
        """
        POST /email — send a single email.

        Args:
            subject: DAG-specific subject (e.g. "my_dag_id failed").
                     CHES_SUBJECT_PREFIX is prepended automatically.
            body:    HTML email body.

        Returns:
            The parsed JSON response from CHES (contains message/transaction IDs).
        """
        full_subject = f"{self._subject_prefix} {subject}".strip()

        payload = {
            "from": self._from_address,
            "to": [self._to_address],
            "subject": full_subject,
            "body": body,
            "bodyType": "html",
        }

        url = f"{self._api_url}/email"
        response = requests.post(
            url,
            json=payload,
            headers=self._auth_headers(),
            timeout=15,
        )

        if not response.ok:
            raise Exception(
                f"Failed to send email: HTTP {response.status_code} — {response.text}"
            )

        print(f"Successfully Sent Email to {self._to_address}")

    def _auth_headers(self):
        """Return headers with a valid Bearer token, refreshing if needed."""
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

    def _get_token(self):
        """Return a cached token, fetching a new one if expired (or close to it)."""
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        self._fetch_token()
        return self._access_token

    def _fetch_token(self):
        """Fetch a new access token from the LoginProxy and cache it."""
        response = requests.post(
            self._login_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )

        if not response.ok:
            raise Exception(
                f"Token request failed: HTTP {response.status_code} — {response.text}"
            )

        data = response.json()
        self._access_token = data["access_token"]
        expires_in = data.get("expires_in", 300)
        self._token_expires_at = time.time() + expires_in - self._TOKEN_REFRESH_BUFFER
        print(f"[CHES] New token acquired, expires in {expires_in}s")
