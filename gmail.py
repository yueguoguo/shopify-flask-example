from __future__ import print_function
import os.path
from email.mime.text import MIMEText
from base64 import urlsafe_b64encode

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send"
]


MESSAGE = """
Hi {customer},\n

Howdy! This is greeting from {shop}. Please review the personalized monthly report for you: \n

In our store, currently we have totally {product_count} products. The top 3 popular products are {product_title_1}, {product_title_2}, and {product_title_3}
"""


def setup_account():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8888)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    return service


def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

    Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    encoded_message = urlsafe_b64encode(message.as_bytes())
    return {'raw': encoded_message.decode()}


def create_draft(service, user_id, message_body):
    """Create and insert a draft email. Print the returned draft's message and id.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message_body: The body of the email message, including headers.

    Returns:
        Draft object, including draft id and message meta data.
    """
    try:
        message = {'message': message_body}
        draft = service.users().drafts().create(userId=user_id, body=message).execute()

        print('Draft id: %s\nDraft message: %s' % (draft['id'], draft['message']))

        return draft
    except Exception as exp:
        print('An error occurred: %s' % str(exp))
        return None


def send_message(service, user_id, message):
    """Send an email message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

    Returns:
        Sent Message.
    """
    try:
        message = (
            service.users().messages().send(userId=user_id, body=message).execute()
        )
        print('Message Id: %s' % message['id'])
        return message
    except Exception as exp:
        print('An error occurred: %s' % str(exp))


if __name__ == '__main__':
    service = setup_account()

    message_body = create_message(
        sender="yueguoguo2048@gmail.com",
        to="yueguoguo1024@gmail.com",
        subject="hello",
        message_text="world"
    )

    send_message(service=service, user_id="me", message=message_body)
