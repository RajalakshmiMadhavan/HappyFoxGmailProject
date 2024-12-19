import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List
from connection import DatabaseService
from config import EMAIL_LABELS

SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.labels']

def authenticate_gmail():
    #authenticates gmail account and avoid authentication when valid creds are available
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'r') as token_file:
            creds_data = json.load(token_file)
            creds = Credentials.from_authorized_user_info(creds_data)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token_file:
            json.dump(json.loads(creds.to_json()), token_file, indent=4)

    return build('gmail', 'v1', credentials=creds)

def fetch_emails(service):
    #fetch emails from gmail service
    all_messages = {}
    for label in EMAIL_LABELS:
        results = service.users().messages().list(userId='me', labelIds=[label], maxResults=10).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print('No messages found.')
        else:
            print('Messages:')
            for message in messages:
                print(message)
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                print(msg)
                email_data = extract_email_data(msg)
                message_id = email_data['message_id']
                if message_id not in all_messages:
                    all_messages[message_id] = email_data
                else:
                    existing_labels = set(all_messages[message_id]['labels'].split(','))
                    new_labels = set(email_data['labels'].split(','))
                    all_messages[message_id]['labels'] = ','.join(existing_labels.union(new_labels))
    return list(all_messages.values())

def extract_email_data(msg):
    message_id = msg['id']
    snippet = msg.get('snippet', '')

    subject = ''
    from_address = ''
    date_received = ''
    labels = msg.get('labelIds', [])
    
    for header in msg['payload']['headers']:
        if header['name'] == 'Subject':
            subject = header['value']
        elif header['name'] == 'From':
            from_address = header['value']
        elif header['name'] == 'Date':
            date_received = header['value']

    return {
        'message_id': message_id,
        'subject': subject,
        'from_address': from_address,
        'date_received': date_received,
        'snippet': snippet,
        'labels': ",".join(labels)
    }

def create_or_update_email_in_db(emails, db_service):
    #create or update the record in db.
    existing_emails = {email['message_id']: email['labels'] for email in DatabaseService().get_all_emails_from_db()}
    for email in emails:
        existing_status = existing_emails.get(email['message_id'])
        if existing_status is not None:
            if set(existing_status.split(',')) != set(email['labels'].split(',')):
                db_service.update_record(email['message_id'], email['labels'])
                print(f"Updated email: {email['message_id']}")
        else:
            DatabaseService().insert_data(email)
            print(f"Inserted new email: {email['message_id']}")

def modify_email(service: object, user_id: int, msg_id: int, msg_labels: dict) -> dict:
    try:
      message = service.users().messages().modify(userId=user_id, id=msg_id,body=msg_labels).execute()
      label_ids = message['labelIds']

      print(f'Message ID: {msg_id} - With Label IDs {label_ids}')
      return message
    except HttpError as error:
      print(f'An error occurred: {error}')

def main():
    service = authenticate_gmail()
    emails = fetch_emails(service)
    db_service = DatabaseService()
    db_service.create_table()
    create_or_update_email_in_db(emails, db_service)

if __name__ == '__main__':
    main()
