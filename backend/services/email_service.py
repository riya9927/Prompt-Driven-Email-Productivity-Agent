import json
import os
from datetime import datetime

class EmailService:
    def __init__(self, database):
        self.db = database
    
    def load_mock_inbox(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)
        mock_inbox_path = os.path.join(backend_dir, 'data', 'mock_inbox.json')
        
        print(f"Looking for mock inbox at: {mock_inbox_path}")
        
        # Create mock inbox if it doesn't exist
        if not os.path.exists(mock_inbox_path):
            print("Mock inbox not found, creating...")
            self._create_mock_inbox()
        
        # Read mock inbox
        print("Reading mock inbox file...")
        with open(mock_inbox_path, 'r', encoding='utf-8') as f:
            emails = json.load(f)
        
        print(f"Loaded {len(emails)} emails from JSON")
        
        # Clear existing emails
        self.db.execute_query('DELETE FROM emails')
        print("Cleared existing emails from database")
        
        # Insert mock emails
        count = 0
        for email in emails:
            self.db.execute_insert(
                '''INSERT INTO emails (sender, subject, body, timestamp)
                   VALUES (?, ?, ?, ?)''',
                (email['sender'], email['subject'], email['body'], email['timestamp'])
            )
            count += 1
        
        print(f"Successfully loaded {count} emails from mock inbox")
        return count
    
    def _create_mock_inbox(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)
        data_dir = os.path.join(backend_dir, 'data')
        mock_inbox_path = os.path.join(data_dir, 'mock_inbox.json')
        
        mock_emails = [
            {
                "sender": "john.doe@company.com",
                "subject": "Q4 Project Meeting - Urgent",
                "body": "Hi team, we need to schedule our Q4 planning meeting ASAP. Can everyone share their availability for next week? We need to finalize the budget by Friday. This is critical for our project timeline.",
                "timestamp": "2024-11-24T09:30:00"
            },
            {
                "sender": "newsletter@techdigest.com",
                "subject": "Weekly Tech News Digest",
                "body": "Here are this week's top technology stories: AI breakthroughs in natural language processing, new smartphone releases from major manufacturers, and the latest cybersecurity updates. Read more about the latest developments in machine learning, cloud computing innovations, and emerging technologies.",
                "timestamp": "2024-11-24T08:00:00"
            },
            {
                "sender": "sales@promosale.com",
                "subject": "LIMITED TIME OFFER - 90% OFF!!!",
                "body": "Click here now to claim your exclusive discount! This offer won't last long! Act fast before it expires! Buy now and save thousands! Don't miss out on this incredible deal! Limited quantities available!",
                "timestamp": "2024-11-24T07:15:00"
            },
            {
                "sender": "sarah.manager@company.com",
                "subject": "Action Required: Timesheet Submission",
                "body": "Please submit your timesheet for the week ending November 22nd by EOD tomorrow. This is required for payroll processing. Make sure all hours are accurately recorded and approved by your supervisor.",
                "timestamp": "2024-11-23T16:45:00"
            },
            {
                "sender": "project.updates@company.com",
                "subject": "Project Alpha - Status Update",
                "body": "Project Alpha is currently 75% complete. Next milestone: Complete testing phase by Nov 30th. Please review the attached progress report and provide feedback by end of week. The team has made excellent progress on the core features.",
                "timestamp": "2024-11-23T14:20:00"
            },
            {
                "sender": "hr@company.com",
                "subject": "Reminder: Annual Review Due",
                "body": "Your annual self-review is due by December 1st. Please complete the form in the HR portal and schedule a meeting with your manager to discuss your performance, achievements, and goals for next year.",
                "timestamp": "2024-11-23T11:00:00"
            },
            {
                "sender": "client@external.com",
                "subject": "Meeting Request - Product Demo",
                "body": "We'd like to schedule a product demonstration for our team. Would you be available sometime next week? We have about 10 stakeholders interested in attending. Please let us know your availability and we can coordinate the schedule.",
                "timestamp": "2024-11-22T15:30:00"
            },
            {
                "sender": "noreply@socialmedia.com",
                "subject": "You have 47 new notifications",
                "body": "Check out what's happening on your social media: 15 likes on your recent post, 12 comments from your friends, 20 friend requests waiting for approval. Click here to see all your notifications and stay connected!",
                "timestamp": "2024-11-22T10:00:00"
            },
            {
                "sender": "support@vendor.com",
                "subject": "Your Support Ticket #12345 - Resolved",
                "body": "Your support ticket regarding the software issue has been resolved. The bug fix will be included in the next release scheduled for December 5th. Please verify the solution works for you and let us know if you need any further assistance.",
                "timestamp": "2024-11-21T14:00:00"
            },
            {
                "sender": "team@company.com",
                "subject": "Team Lunch - Friday 12:30 PM",
                "body": "Join us for team lunch this Friday at 12:30 PM at the Italian restaurant downtown. Please RSVP by Thursday so we can make a reservation. Looking forward to seeing everyone there!",
                "timestamp": "2024-11-21T09:00:00"
            },
            {
                "sender": "finance@company.com",
                "subject": "Expense Report Approval Needed",
                "body": "Your expense report for October travel is pending approval. Please review the submitted expenses and approve or reject them by end of week. Total amount: $1,247.89. Any questions, please contact the finance team.",
                "timestamp": "2024-11-20T16:00:00"
            },
            {
                "sender": "training@company.com",
                "subject": "Mandatory Security Training",
                "body": "All employees must complete the cybersecurity training module by November 30th. The training takes approximately 2 hours and covers important security protocols, phishing awareness, and data protection. Login to the training portal to get started.",
                "timestamp": "2024-11-20T10:30:00"
            }
        ]
        
        os.makedirs(data_dir, exist_ok=True)
        print(f"Creating mock inbox at: {mock_inbox_path}")
        
        with open(mock_inbox_path, 'w', encoding='utf-8') as f:
            json.dump(mock_emails, f, indent=2)
        
        print(f"Created mock inbox file at {mock_inbox_path}")
    
    def get_all_emails(self):
        rows = self.db.execute_query('SELECT * FROM emails ORDER BY timestamp DESC')
        emails = []
        
        for row in rows:
            email = self.db.row_to_dict(row)
            if email['action_items']:
                try:
                    email['action_items'] = json.loads(email['action_items'])
                except json.JSONDecodeError:
                    email['action_items'] = []
            else:
                email['action_items'] = []
            emails.append(email)
        
        return emails
    
    def get_email_by_id(self, email_id):
        rows = self.db.execute_query('SELECT * FROM emails WHERE id = ?', (email_id,))
        
        if rows:
            email = self.db.row_to_dict(rows[0])
            if email['action_items']:
                try:
                    email['action_items'] = json.loads(email['action_items'])
                except json.JSONDecodeError:
                    email['action_items'] = []
            else:
                email['action_items'] = []
            return email
        
        return None
    
    def update_email(self, email_id, category=None, action_items=None):
        if action_items:
            action_items_json = json.dumps(action_items)
        else:
            action_items_json = None
        
        self.db.execute_query(
            '''UPDATE emails 
               SET category = ?, action_items = ?, processed = 1
               WHERE id = ?''',
            (category, action_items_json, email_id)
        )
    
    def get_emails_by_category(self, category):
        rows = self.db.execute_query(
            'SELECT * FROM emails WHERE category = ? ORDER BY timestamp DESC',
            (category,)
        )
        
        emails = []
        for row in rows:
            email = self.db.row_to_dict(row)
            if email['action_items']:
                try:
                    email['action_items'] = json.loads(email['action_items'])
                except:
                    email['action_items'] = []
            else:
                email['action_items'] = []
            emails.append(email)
        
        return emails
    
    def search_emails(self, query):
        search_pattern = f"%{query}%"
        rows = self.db.execute_query(
            '''SELECT * FROM emails 
               WHERE subject LIKE ? OR body LIKE ? OR sender LIKE ?
               ORDER BY timestamp DESC''',
            (search_pattern, search_pattern, search_pattern)
        )
        
        emails = []
        for row in rows:
            email = self.db.row_to_dict(row)
            if email['action_items']:
                try:
                    email['action_items'] = json.loads(email['action_items'])
                except:
                    email['action_items'] = []
            else:
                email['action_items'] = []
            emails.append(email)
        return emails
    
    
    def get_all_drafts(self):
        rows = self.db.execute_query('SELECT * FROM drafts ORDER BY created_at DESC')
        drafts = []
        
        for row in rows:
            draft = self.db.row_to_dict(row)
            # Parse metadata JSON if it exists
            if draft['metadata']:
                try:
                    draft['metadata'] = json.loads(draft['metadata'])
                except json.JSONDecodeError:
                    draft['metadata'] = {}
            else:
                draft['metadata'] = {}
            drafts.append(draft)
        
        return drafts
    
    def get_draft_by_id(self, draft_id):
        rows = self.db.execute_query('SELECT * FROM drafts WHERE id = ?', (draft_id,))
        
        if rows:
            draft = self.db.row_to_dict(rows[0])
            if draft['metadata']:
                try:
                    draft['metadata'] = json.loads(draft['metadata'])
                except:
                    draft['metadata'] = {}
            else:
                draft['metadata'] = {}
            return draft
        
        return None
    
    def create_draft(self, email_id, subject, body, metadata=None):
        metadata_json = json.dumps(metadata) if metadata else None
        
        draft_id = self.db.execute_insert(
            '''INSERT INTO drafts (email_id, subject, body, metadata)
               VALUES (?, ?, ?, ?)''',
            (email_id, subject, body, metadata_json)
        )
        
        print(f"Created draft with ID: {draft_id}")
        return draft_id
    
    def update_draft(self, draft_id, subject=None, body=None, metadata=None):
        draft = self.db.execute_query('SELECT * FROM drafts WHERE id = ?', (draft_id,))
        
        if not draft:
            raise ValueError(f"Draft with ID {draft_id} not found")
        
        current = self.db.row_to_dict(draft[0])
        
        subject = subject if subject is not None else current['subject']
        body = body if body is not None else current['body']
        metadata_json = json.dumps(metadata) if metadata is not None else current['metadata']
        
        self.db.execute_query(
            '''UPDATE drafts 
               SET subject = ?, body = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (subject, body, metadata_json, draft_id)
        )
        
        print(f"Updated draft with ID: {draft_id}")
    
    def delete_draft(self, draft_id):
        self.db.execute_query('DELETE FROM drafts WHERE id = ?', (draft_id,))
        print(f"Deleted draft with ID: {draft_id}")
    
    def get_drafts_for_email(self, email_id):
        rows = self.db.execute_query(
            'SELECT * FROM drafts WHERE email_id = ? ORDER BY created_at DESC',
            (email_id,)
        )
        
        drafts = []
        for row in rows:
            draft = self.db.row_to_dict(row)
            if draft['metadata']:
                try:
                    draft['metadata'] = json.loads(draft['metadata'])
                except:
                    draft['metadata'] = {}
            else:
                draft['metadata'] = {}
            drafts.append(draft)
        
        return drafts

    def get_email_statistics(self):
        stats = {
            'total': 0,
            'processed': 0,
            'unprocessed': 0,
            'by_category': {
                'Important': 0,
                'Newsletter': 0,
                'Spam': 0,
                'To-Do': 0
            },
            'total_action_items': 0
        }
        
        emails = self.get_all_emails()
        stats['total'] = len(emails)
        
        for email in emails:
            if email.get('processed'):
                stats['processed'] += 1
            else:
                stats['unprocessed'] += 1
            
            category = email.get('category')
            if category and category in stats['by_category']:
                stats['by_category'][category] += 1
            
            if email.get('action_items'):
                stats['total_action_items'] += len(email['action_items'])
        
        return stats

if __name__ == '__main__':
    import sys
    sys.path.append('..')
    from models.database import Database
    
    # Initialize
    db = Database()
    db.initialize()
    email_service = EmailService(db)
    
    # Load mock inbox
    count = email_service.load_mock_inbox()
    print(f"Loaded {count} emails")
    
    # Get all emails
    emails = email_service.get_all_emails()
    print(f"\nFound {len(emails)} emails:")
    for email in emails[:3]:
        print(f"  - {email['sender']}: {email['subject']}")
    
    # Update an email
    if emails:
        email_service.update_email(
            emails[0]['id'],
            category='Important',
            action_items=[{'task': 'Test task', 'deadline': 'Tomorrow'}]
        )
        print(f"\nUpdated email ID {emails[0]['id']}")
    
    # Get statistics
    stats = email_service.get_email_statistics()
    print(f"\n Email Statistics:")
    print(f"  Total: {stats['total']}")
    print(f"  Processed: {stats['processed']}")
    print(f"  Action Items: {stats['total_action_items']}")
    
    # Create a draft
    if emails:
        draft_id = email_service.create_draft(
            email_id=emails[0]['id'],
            subject=f"Re: {emails[0]['subject']}",
            body="Thank you for your email. I will get back to you shortly.",
            metadata={'generated': True, 'timestamp': datetime.now().isoformat()}
        )
        print(f"\nCreated draft with ID: {draft_id}")
    
    # Get all drafts
    drafts = email_service.get_all_drafts()
    print(f"\nFound {len(drafts)} draft(s)")
    
    # Search emails
    search_results = email_service.search_emails('meeting')
    print(f"\nSearch for 'meeting' found {len(search_results)} result(s)")
    