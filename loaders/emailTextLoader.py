import base64
import contextlib
import json
import os.path
import re
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def clean_text(text):
    soup = BeautifulSoup(text, "html.parser")
    input_string = soup.get_text()

    # Replace Unicode characters
    input_string = re.sub(r"\\u[0-9a-fA-F]{4}", "", input_string)

    # Remove newline characters
    input_string = input_string.replace("\n", "").replace("\u00a0\u200c", "")

    input_string = re.sub(r"\r\s+", "", input_string)

    return input_string


def get_emails():
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    one_day_ago = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                # your creds file here. Please create json file as here https://cloud.google.com/docs/authentication/getting-started
                "credentials.json",
                SCOPES,
            )
            creds = flow.run_local_server(port=8500)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)

        query = f"after:{one_day_ago}"

        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], q=query)
            .execute()
        )
        if messages := results.get("messages", []):
            message_count = 0
            clean_messages = []
            for message in messages:
                message_count += 1
                clean_message = {}
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=message["id"])
                    .execute()
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
                clean_messages.append(clean_message)
            corpora = ""
            for message in clean_messages:
                corpora += message["text"] + ". "
            return corpora
        else:
            return []
    except Exception as error:
        print(f"An error occurred: {error}")
