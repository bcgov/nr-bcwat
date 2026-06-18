import os
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class CHESClient:

    def __init__(self):
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
            # "to": [self._to_address],
            "to": ["liam@foundryspatial.com"],
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
            "Authorization": f"Bearer {self._fetch_token()}",
            "Content-Type": "application/json",
        }
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
        return data["access_token"]
