FIELD_VALUE_MAPPINGS = {
    'Subject': 'subject',
    'From': 'from_email',
    'Received': 'date_received'
}

PREDICATE_MAPPINGS = {
    'Contains': "in",
    'Does not Contain': "not in", 
    'Equals': "==",
    'Does not equal': "!=",
    'Less than': "<",
    'Greater than': ">"
}

ACTION_LABEL_MAPPINGS = {
    'unread': 'addLabelIds',
    'read': 'removeLabelIds'
}

EMAIL_LABELS = ['INBOX', 'TRASH', 'UNREAD', 'STARRED', 'IMPORTANT']