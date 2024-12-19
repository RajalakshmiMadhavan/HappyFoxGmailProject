import sqlite3
import json
connection = sqlite3.connect('emails.db')
cursor = connection.cursor()

class DatabaseService:

    def __init__(self, db_path='emails.db'):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def get_connection(self):
        return self.connection

    def create_table(self):

      create_table_query = '''
        CREATE TABLE IF NOT EXISTS emails (
           id INT AUTO_INCREMENT PRIMARY KEY,
           message_id VARCHAR(255),
           subject VARCHAR(255),
           from_email VARCHAR(255),
           date_received DATETIME,
           snippet TEXT,
           labels JSON
        );
        '''
      cursor.execute(create_table_query)
      connection.commit()
    
    def insert_data(self, email):
        insert_query = '''INSERT INTO emails
                           (message_id, subject, from_email, date_received, snippet, labels)
                            VALUES (?, ?, ?, ?, ?, ?)'''
        cursor.execute(insert_query, (email['message_id'], email['subject'], email['from_address'], 
                            email['date_received'], email['snippet'], email['labels']))
        connection.commit()

    def update_record(self, message_id, labels):
        conn = self.get_connection()
        cursor = conn.cursor()
        update_query = ''' UPDATE emails SET labels = ? WHERE message_id = ?;'''
        cursor.execute(update_query, (json.dumps(labels), message_id))
        connection.commit()
    
    def get_all_emails_from_db(self):
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM emails")
        rows = cursor.fetchall()
        emails = [
        {
            'message_id': row['message_id'],
            'subject': row['subject'],
            'from_email': row['from_email'],
            'date_received': row['date_received'],
            'snippet': row['snippet'],
            'labels': row['labels']
        }
        for row in rows
       ]    
        connection.commit()
        return emails
    
    def enable_wal(self):
        try:
            self.cursor.execute("PRAGMA journal_mode=WAL;")
            wal_mode = self.cursor.fetchone()
            print(f"WAL mode enabled: {wal_mode[0]}")
        except sqlite3.Error as e:
            print(f"An error occurred while enabling WAL mode: {e}")

    def close(self):
        self.connection.close()
    