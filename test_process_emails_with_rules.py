import unittest
from unittest.mock import patch, Mock, MagicMock
import sqlite3
import os
import json
from gmail_oauth import (
    authenticate_gmail, fetch_emails, extract_email_data, modify_email
)
from process_emails_with_rules import evaluate_rule
from connection import DatabaseService

from process_emails_with_rules import (apply_actions, process_email)
RULES = [
    {
        "predicate": "All",
        "conditions": [
            {"field": "From", "predicate": "Contains", "value": "test@example.com"},
            {"field": "Subject", "predicate": "Contains", "value": "Test Subject"}
        ],
        "actions": {
            "mark_as": "read",
            "move_message": "INBOX"
        }
    }
]

class TestGmailCase(unittest.TestCase):
    def setUp(self):         
        self.db_service = DatabaseService(db_path='test_emails.db')
        self.service_mock = Mock()

        with self.db_service.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS emails (
                message_id TEXT PRIMARY KEY,
                subject TEXT,
                from_address TEXT,
                date_received TEXT,
                snippet TEXT,
                labels TEXT
            )''')
            
            self.test_email = {
                'message_id': '12345',
                'subject': 'Test Subject',
                'from_email': 'test@example.com',
                'date_received': 'Mon, 1 Jan 2024 10:00:00',
                'snippet': 'Test email snippet',
                'labels': 'UNREAD',
            }
            
            insert_query = '''INSERT OR REPLACE INTO emails (message_id, subject, from_address, date_received, snippet, labels)
                              VALUES (?, ?, ?, ?, ?, ?)'''
            cursor.execute(insert_query, tuple(self.test_email.values()))
            conn.commit()
    
    def tearDown(self):
        with self.db_service.get_connection() as conn:
          cursor = conn.cursor()
          cursor.execute('DROP TABLE IF EXISTS emails')
          conn.commit()
    
    def test_all_conditions_pass(self):
        rule = {
            "predicate": "All",
            "conditions": [
                {"field": "From", "predicate": "Contains", "value": "test@example.com"},
                {"field": "Subject", "predicate": "Contains", "value": "Test Subject"}
            ]
        }
        result = evaluate_rule(self.test_email, rule)
        self.assertTrue(result)
    
    def test_all_conditions_fail(self):
        rule = {
            "predicate": "All",
            "conditions": [
                {"field": "From", "predicate": "Contains", "value": "nonexistent@example.com"},
                {"field": "Subject", "predicate": "Contains", "value": "Different Subject"}
            ]
        }
        result = evaluate_rule(self.test_email, rule)
        self.assertFalse(result)
    
    def test_any_condition_pass(self):
        rule = {
            "predicate": "Any",
            "conditions": [
                {"field": "From", "predicate": "Contains", "value": "nonexistent@example.com"},
                {"field": "Subject", "predicate": "Contains", "value": "Test Subject"}
            ]
        }
        result = evaluate_rule(self.test_email, rule)
        self.assertTrue(result)
    
    def test_any_condition_fail(self):
        rule = {
            "predicate": "Any",
            "conditions": [
                {"field": "From", "predicate": "==", "value": "nonexistent@example.com"},
                {"field": "Subject", "predicate": "==", "value": "Different Subject"}
            ]
        }
        result = evaluate_rule(self.test_email, rule)
        self.assertFalse(result) 
    
    @patch("gmail_oauth.authenticate_gmail")
    def test_process_email_with_rules(self, mock_authenticate_gmail):
        message_id = "12345"
        service_mock = Mock()
        mock_modify = Mock()
        self.mock_modify_email(mock_authenticate_gmail, service_mock, mock_modify)
        process_email(self.test_email, RULES, service_mock, self.db_service)
        self.assertEqual(mock_modify.execute.call_count, 2)
        select_query = '''SELECT labels FROM emails WHERE message_id = ?;'''
        with self.db_service.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(select_query, (message_id,))
            rows = cursor.fetchall()
            labels_list = json.loads(rows[0][0]) if rows[0][0] else []
            self.assertNotIn('UNREAD', labels_list)
            self.assertEqual(['INBOX', 'READ'], labels_list)
    
    def mock_modify_email(self, mock_authenticate_gmail, service_mock, mock_modify):
        mock_users = Mock()
        mock_messages = Mock()
        mock_authenticate_gmail.return_value = service_mock
        service_mock.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.modify.return_value = mock_modify
        mock_modify.execute.return_value = {'labelIds': ['INBOX', 'READ']}