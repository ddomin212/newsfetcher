import base64
import contextlib
import os.path
import re
from datetime import datetime, timedelta
from typing import Any

from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


def clean_text(text: str) -> str:
    """Clean the text from the email and remove all the unnecessary characters (mainly HTML tags and unicode characters)

    Arguments:
        text {str} -- The text from the email

    Returns:
        str -- The cleaned text"""
    soup = BeautifulSoup(text, "html.parser")
    input_string = soup.get_text()

    input_string = re.sub(r"\\u[0-9a-fA-F]{4}", "", input_string)

    input_string = input_string.replace("\n", "").replace("\u00a0\u200c", "")

    input_string = re.sub(r"\r\s+", "", input_string)

    return input_string


def google_authenticate(creds: Credentials) -> None:
    """Refresh google OAuth 2 credentials if they are expired or create new ones if they don't exist

    Arguments:
        creds {Credentials} -- The OAuth 2 credentials"""
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES,
        )
        creds = flow.run_local_server(port=8500)
    with open("token.json", "w") as token:
        token.write(creds.to_json())


def parse_mail_body(
    service: Any, message: dict[str, dict | str]
) -> dict[str, str]:
    """Parse the email body and return the email sender name and the email body text

    Arguments:
        service {Any} -- The Gmail API service
        message {dict} -- The email message"""
    clean_message = {}
    msg = (
        service.users().messages().get(userId="me", id=message["id"]).execute()
    )
    email_data = msg["payload"]["headers"]
    for values in email_data:
        name = values["name"]
        if name == "From":
            from_name = values["value"]
            clean_message["from"] = from_name
            if "parts" in msg["payload"].keys():
                for part in msg["payload"]["parts"]:
                    with contextlib.suppress(BaseException):
                        data = part["body"]["data"]
                        byte_code = base64.urlsafe_b64decode(data)

                        text = byte_code.decode("utf-8")

                        clean_message["text"] = clean_text(text)
    return clean_message


def fetch_emails(service: Any, time_ago: str) -> str:
    """Fetch the emails from the last X time and return them as a string

    Arguments:
        service {Any} -- The Gmail API service
        time_ago {str} -- The date which is X time ago
    """
    query = f"after:{time_ago}"

    results = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], q=query)
        .execute()
    )
    if messages := results.get("messages", []):
        corpora = ""
        for message in messages:
            clean_message = parse_mail_body(service, message)
            corpora += clean_message["text"] + ". "
        return corpora
    else:
        return ""


def get_emails_yesterday() -> str:
    """Fetch the emails from the last 24 hours and return them as a string

    Returns:
        str -- The emails from the last 24 hours as a string
    """
    one_day_ago = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        google_authenticate(creds)

    try:
        service = build("gmail", "v1", credentials=creds)
        return fetch_emails(service, one_day_ago)
    except Exception as error:
        print(f"An error occurred: {error}")
