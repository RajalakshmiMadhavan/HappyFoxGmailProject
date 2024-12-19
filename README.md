# HappyFoxGmailProject
Python script that integrates with GMAIL API, apply rules and actions.

1. Add a new project in Google cloud console and register your gmail test account.
2. Enable GMAIL API for your test project.
3. Give permission to read and write to test account.
4. Once registration is done, Google cloud console gives you the credentials.json file. Copy and attach to your project.
5. Run this ```pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib``` to install google python's library
6. Run ```gmail_oauth.py``` to authenticate gmail account for the first time. ```token.json``` will be created and credentials will be added. ```emails.db``` will be created.
7. All emails will be fetched from gmail account and inserted into the table. If records are existing already, it will be updated.
8. Run ```process_emails_with_rules.py``` to apply rules and actions. Modify the ```rules.json``` to test for other scenarios.
9. Added test cases, ```test_gmail_oauth.py``` which tests gmail authentication and fetch emails from gmail account.
10. Another file ```test_process_emails_with_rules.py``` which tests with various conditions will ALL, AND predicate and apply actions.
11. Run test file using ```python -m unittest test_gmail_oauth.py``` and ```python -m uniitest test_process_emails_with_rules.py```
