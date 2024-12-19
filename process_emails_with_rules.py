import json
from datetime import datetime
from googleapiclient.errors import HttpError
import time
from config import FIELD_VALUE_MAPPINGS, PREDICATE_MAPPINGS, ACTION_LABEL_MAPPINGS
from gmail_oauth import authenticate_gmail, modify_email
from connection import DatabaseService
import pdb

def process_email(email, rules, service, db_service):
    try:
        for rule in rules:
            if evaluate_rule(email, rule):
                print(f"Rule matched for email: {email['message_id']}")
                apply_actions(rule['actions'], email['message_id'], service, db_service)
                break
    except HttpError as error:
        print(f'An error occurred: {error}')

def evaluate_rule(email, rule):
    for condition in rule['conditions']:
        db_name = FIELD_VALUE_MAPPINGS.get(condition['field'])
        db_value = email.get(db_name)
        if not apply_condition(db_value, condition['predicate'], condition['value']):
            if rule['predicate'] == 'All':
                return False
        else:
            if rule['predicate'] == 'Any':
                return True
    return rule['predicate'] == 'All'

def apply_condition(db_value, predicate, value):
    operator = PREDICATE_MAPPINGS.get(predicate)
    if operator:
        if operator in ["in", "not in", "==", "!="]:
           return eval(f"'{value}' {operator} '{db_value}'")
        if operator == '<':
            field_date = datetime.strptime(db_value, "%a, %d %b %Y %H:%M:%S %z")
            current_time = int(time.time() * 1000)
            previous = current_time - ((int(value)*24) * 60 * 60 * 1000)
            return field_date.timestamp()*1000 < previous
        if operator == '>':
            field_date = datetime.strptime(db_value, "%a, %d %b %Y %H:%M:%S %z")
            current_time = int(time.time() * 1000)
            modified_time = current_time - ((int(value)*24) * 60 * 60 * 1000)
            return field_date.timestamp()*1000 > modified_time
    return False

def apply_actions(actions, message_id, service, db_service):
    try:        
        for action_key, action_value in actions.items():
            if action_key == "mark_as":
              label = ACTION_LABEL_MAPPINGS.get(action_value)
              message = modify_email(service, 'me', message_id, {label: ['UNREAD']})
              db_service.update_record(message_id, message['labelIds'])
              print(f"Action {action_value} applied to message {message_id}")
            elif action_key == "move_message":
              message = modify_email(service, 'me', message_id, {'addLabelIds': [action_value]})
              db_service.update_record(message_id, message['labelIds'])
    except HttpError as error:
        print(f'An error occurred while applying actions: {error}')

def load_rules(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def main():
    rules = load_rules('rules.json')
    
    db_service = DatabaseService()
    service = authenticate_gmail()
    emails = db_service.get_all_emails_from_db()
    if not emails:
        print('No emails found.')
    else:
        for email in emails:
            process_email(email, rules, service, db_service)

if __name__ == '__main__':
    main()
