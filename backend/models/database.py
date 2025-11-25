import sqlite3
import json
import os
from datetime import datetime


class Database:
    def __init__(self, db_path='data/email_agent.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  
        return conn
    
    def initialize(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create emails table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                category TEXT,
                action_items TEXT,
                processed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create prompts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_type TEXT UNIQUE NOT NULL,
                prompt_text TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create drafts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails(id)
            )
        ''')
        
        # Initialize default prompts if they don't exist
        default_prompts = [
            (
                'categorization',
                'Categorize emails into: Important, Newsletter, Spam, To-Do. '
                'To-Do emails must include a direct request requiring user action. '
                'Important emails are urgent matters needing attention. '
                'Newsletters are informational digests. '
                'Spam includes promotional and unwanted messages.'
            ),
            (
                'action_item',
                'Extract tasks from the email. Respond in JSON format: '
                '[{"task": "description of task", "deadline": "when it is due"}]. '
                'Only extract clear, actionable items that require user action. '
                'If no tasks are found, return an empty array [].'
            ),
            (
                'auto_reply',
                'Draft a professional reply to this email. '
                'If it is a meeting request, ask for an agenda and confirm interest. '
                'If it is a task request, acknowledge receipt and provide a timeline. '
                'Otherwise, draft an appropriate professional response. '
                'Keep the tone friendly but professional.'
            )
        ]
        
        for prompt_type, prompt_text in default_prompts:
            cursor.execute('''
                INSERT OR IGNORE INTO prompts (prompt_type, prompt_text)
                VALUES (?, ?)
            ''', (prompt_type, prompt_text))
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
        print(f"Database location: {os.path.abspath(self.db_path)}")
    
    def execute_query(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            conn.commit()
            return results
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_insert(self, query, params):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            last_id = cursor.lastrowid
            conn.commit()
            return last_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def row_to_dict(self, row):
        if row is None:
            return None
        return {key: row[key] for key in row.keys()}
    
    def clear_table(self, table_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM {table_name}')
        conn.commit()
        conn.close()
    
    def get_table_count(self, table_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f'SELECT COUNT(*) as count FROM {table_name}')
        result = cursor.fetchone()
        conn.close()
        return result['count'] if result else 0

if __name__ == '__main__':
    # Initialize database
    db = Database()
    db.initialize()
    
    # Insert a test email
    email_id = db.execute_insert(
        '''INSERT INTO emails (sender, subject, body, timestamp)
           VALUES (?, ?, ?, ?)''',
        ('test@example.com', 'Test Subject', 'Test body', '2024-11-24T10:00:00')
    )
    print(f"Inserted test email with ID: {email_id}")
    
    # Query emails
    emails = db.execute_query('SELECT * FROM emails')
    print(f"Found {len(emails)} email(s)")
    
    # Get prompts
    prompts = db.execute_query('SELECT * FROM prompts')
    print(f"Found {len(prompts)} prompt(s)")
    for prompt in prompts:
        prompt_dict = db.row_to_dict(prompt)
        print(f"  - {prompt_dict['prompt_type']}")
    
    # Get table counts
    print(f"\nEmails count: {db.get_table_count('emails')}")
    print(f"Prompts count: {db.get_table_count('prompts')}")
    print(f"Drafts count: {db.get_table_count('drafts')}")