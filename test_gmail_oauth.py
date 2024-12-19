import unittest
from unittest.mock import patch, Mock, MagicMock
from gmail_oauth import (authenticate_gmail, extract_email_data, fetch_emails)
class TestGmailOauth(unittest.TestCase):
    @patch('gmail_oauth.build')
    def test_authenticate_gmail(self, mock_build):
        mock_build.return_value = Mock()
        service = authenticate_gmail()
        self.assertIsNotNone(service)
        mock_build.assert_called_once_with('gmail', 'v1', credentials=unittest.mock.ANY)
    
    @patch('gmail_oauth.EMAIL_LABELS', ['INBOX', 'IMPORTANT'])
    @patch('gmail_oauth.authenticate_gmail')
    def test_fetch_emails(self, mock_authenticate_gmail):
        mock_service = MagicMock()
        mock_authenticate_gmail.return_value = mock_service
        mock_service.users().messages().list().execute.return_value = { 'messages': [{'id': '12345'}] }
        mock_service.users().messages().get(user_id='me', id='12345').execute.return_value = {
                'id': '12345',
                'snippet': 'Test Snippet 1',
                'labelIds': ['INBOX'],
                'payload': {
                    'headers': [
                        {'name': 'Subject', 'value': 'Test Subject 1'},
                        {'name': 'From', 'value': 'test1@example.com'},
                        {'name': 'Date', 'value': 'Wed, 18 Dec 2024 12:00:00 +0000'}
                    ]
                }
            }
        emails = fetch_emails(mock_service)
        self.assertEqual(emails[0]['message_id'], '12345')
        self.assertEqual(emails[0]['subject'], 'Test Subject 1')
