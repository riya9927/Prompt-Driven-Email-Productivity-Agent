# Email Productivity Agent

An intelligent, prompt-driven Email Productivity Agent powered by Claude AI that automates email management through categorization, action-item extraction, and auto-drafting replies.

## 🌟 Features

- **Email Categorization**: Automatically categorizes emails into Important, Newsletter, Spam, or To-Do
- **Action Item Extraction**: Identifies and extracts tasks with deadlines from emails
- **Auto-Reply Drafts**: Generates professional reply drafts based on email context
- **Chat Interface**: Interactive agent for querying and managing your inbox
- **Prompt Configuration**: Fully customizable AI behavior through editable prompts
- **Mock Inbox**: Pre-loaded sample emails for testing and demonstration

## 📋 Requirements

- Python 3.8+
- Anthropic API Key (optional - system works with mock responses)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd email-productivity-agent
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional)
# Add your Anthropic API key if you have one
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env

# Run the backend server
python app.py
```

The backend will start at `http://localhost:5000`

### 3. Frontend Setup (New Terminal)

```bash
# Navigate to project root
cd email-productivity-agent

# Install frontend dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run streamlit_app.py
```

The frontend will open automatically in your browser at `http://localhost:8501`

## 📁 Project Structure

```
email-productivity-agent/
├── backend/
│   ├── app.py                      # Flask API server
│   ├── requirements.txt            # Backend dependencies
│   ├── models/
│   │   └── database.py            # Database operations
│   ├── services/
│   │   ├── email_service.py       # Email management logic
│   │   ├── llm_service.py         # AI/LLM integration
│   │   └── prompt_service.py      # Prompt management
│   └── data/
│       ├── email_agent.db         # SQLite database (auto-created)
│       └── mock_inbox.json        # Sample emails (auto-created)
├── streamlit_app.py                # Streamlit UI
├── requirements.txt                # Frontend dependencies
├── .env                            # Environment variables
└── README.md                       # This file
```

## 🎯 Usage Guide

### Loading the Mock Inbox

1. Click **"Load Mock Inbox"** in the sidebar
2. 12 sample emails will be loaded into the system
3. View emails in the **Inbox** tab

### Processing Emails

1. Click **"Process All Emails"** to categorize and extract action items
2. AI will analyze each email using your configured prompts
3. Results appear as colored badges and task lists

### Using the Email Agent

1. Go to the **Email Agent** tab
2. Type queries like:
   - "What are my urgent emails?"
   - "List all my tasks"
   - "Summarize this email" (select email first)
   - "Draft a reply to this email"
3. Use Quick Action buttons for common tasks

### Managing Drafts

1. Go to the **Drafts** tab
2. Generate drafts via the Email Agent
3. Edit subject and body as needed
4. Drafts are stored, never sent automatically

### Configuring Prompts

1. Go to **Prompt Configuration** tab
2. Edit the three main prompts:
   - **Categorization**: How emails are classified
   - **Action Item Extraction**: How tasks are identified
   - **Auto-Reply**: How responses are drafted
3. Click **Save Prompts** to apply changes

## 🔧 Configuration

### Prompt Templates

**Default Categorization Prompt:**
```
Categorize emails into: Important, Newsletter, Spam, To-Do.
To-Do emails must include a direct request requiring user action.
```

**Default Action Item Prompt:**
```
Extract tasks from the email. Respond in JSON format:
{ "task": "...", "deadline": "..." }.
```

**Default Auto-Reply Prompt:**
```
If an email is a meeting request, draft a polite reply asking for an agenda.
Otherwise, draft an appropriate professional response.
```

### Environment Variables

Create a `.env` file in the backend directory:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

**Note:** If no API key is provided, the system uses mock responses for testing.

## 🔌 API Endpoints

### Emails
- `GET /api/emails` - Get all emails
- `GET /api/emails/<id>` - Get specific email
- `POST /api/emails/load` - Load mock inbox
- `POST /api/emails/process` - Process emails with AI

### Prompts
- `GET /api/prompts` - Get all prompts
- `GET /api/prompts/<type>` - Get specific prompt
- `PUT /api/prompts` - Update prompts

### Agent
- `POST /api/agent/chat` - Chat with email agent

### Drafts
- `GET /api/drafts` - Get all drafts
- `POST /api/drafts` - Create draft
- `PUT /api/drafts/<id>` - Update draft
- `DELETE /api/drafts/<id>` - Delete draft
- `POST /api/drafts/generate` - Generate AI draft

## 🎬 Demo Video Script

A 5-10 minute demo should cover:

1. **Introduction (1 min)**
   - Show the UI overview
   - Explain the three main tabs

2. **Loading Inbox (1 min)**
   - Click "Load Mock Inbox"
   - Show the 12 sample emails loaded

3. **Prompt Configuration (2 min)**
   - Navigate to Prompt Configuration
   - Show the three default prompts
   - Edit one prompt (e.g., add new category)
   - Save changes

4. **Email Processing (2 min)**
   - Click "Process All Emails"
   - Show emails being categorized
   - Display action items extracted
   - View different categories (Important, To-Do, Newsletter, Spam)

5. **Email Agent Chat (2-3 min)**
   - Ask "What are my urgent emails?"
   - Ask "List all my tasks"
   - Select an email
   - Ask "Summarize this email"
   - Ask "Draft a reply"

6. **Draft Management (1 min)**
   - Go to Drafts tab
   - Show generated draft
   - Edit the draft
   - Explain that drafts are never sent automatically

## 🧪 Testing Without API Key

The system includes mock LLM responses for testing without an Anthropic API key:

- Categories are assigned based on keyword matching
- Action items are extracted using pattern recognition
- Draft replies use template-based generation

This allows full demonstration of functionality without API costs.

## 🛡️ Safety Features

- **No Auto-Sending**: Drafts are stored, never sent automatically
- **Error Handling**: Graceful degradation if LLM fails
- **Mock Mode**: Full functionality without API key
- **Data Persistence**: SQLite database for reliable storage

## 🐛 Troubleshooting

### Backend won't start
- Check if port 5000 is available
- Ensure all dependencies are installed
- Verify Python version (3.8+)

### Frontend can't connect
- Ensure backend is running at localhost:5000
- Check CORS settings in app.py
- Verify firewall settings

### LLM not working
- Check if ANTHROPIC_API_KEY is set in .env
- Verify API key is valid
- System works with mock responses if key is missing

### Database errors
- Delete `data/email_agent.db` and restart
- Check write permissions in data/ directory

## 📝 Mock Inbox Content

The mock inbox includes:
- Urgent project meeting requests
- Newsletters and digests
- Spam/promotional emails
- Action-required tasks (timesheets, reviews)
- Client meeting requests
- Social media notifications
- Team event invitations
- Training reminders

## 🔄 Development

### Adding New Email Sources

Edit `services/email_service.py` to add new email sources:

```python
def load_from_gmail(self):
    # Implement Gmail API integration
    pass
```

### Custom Prompts

Add new prompt types in the database:

```python
prompt_service.create_prompt('sentiment', 'Analyze email sentiment...')
```

### Extending the Agent

Add new chat commands in `services/llm_service.py`:

```python
if 'schedule' in query_lower:
    # Handle scheduling logic
    pass
```

## 📦 Dependencies

### Backend
- Flask 3.0.0 - Web framework
- Flask-CORS 4.0.0 - Cross-origin requests
- Anthropic 0.39.0 - Claude AI integration
- Python-dotenv 1.0.0 - Environment management

### Frontend
- Streamlit 1.29.0 - Web UI framework
- Requests 2.31.0 - HTTP client

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is created for educational purposes.

## 🙏 Acknowledgments

- Built with Claude AI by Anthropic
- UI powered by Streamlit
- Backend using Flask

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Open an issue on GitHub

---
