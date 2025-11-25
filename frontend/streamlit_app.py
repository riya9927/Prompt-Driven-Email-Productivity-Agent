import streamlit as st
import requests
import json
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Email Productivity Agent",
    page_icon="📧",
    layout="wide"
)

# Backend API URL
API_URL = "http://localhost:5000/api"

# Initialize session state
if 'selected_email' not in st.session_state:
    st.session_state.selected_email = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'last_selected_email_id' not in st.session_state:
    st.session_state.last_selected_email_id = None

def load_inbox():
    try:
        response = requests.post(f"{API_URL}/emails/load")
        if response.status_code == 200:
            st.success(f"{response.json()['message']}")
            # Clear chat when loading new inbox
            st.session_state.chat_messages = []
            st.session_state.selected_email = None
            st.session_state.last_selected_email_id = None
            st.rerun()
        else:
            st.error(f"Error loading inbox: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")

def get_emails():
    try:
        response = requests.get(f"{API_URL}/emails")
        if response.status_code == 200:
            return response.json()['emails']
        return []
    except Exception as e:
        st.error(f"Error fetching emails: {str(e)}")
        return []

def process_emails():
    try:
        with st.spinner("Processing emails with AI..."):
            response = requests.post(f"{API_URL}/emails/process")
            if response.status_code == 200:
                st.success("Emails processed successfully!")
                st.rerun()
            else:
                st.error(f"Error processing emails: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def get_prompts():
    try:
        response = requests.get(f"{API_URL}/prompts")
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        st.error(f"Error fetching prompts: {str(e)}")
        return {}

def update_prompts(prompts):
    try:
        response = requests.put(f"{API_URL}/prompts", json=prompts)
        if response.status_code == 200:
            st.success("Prompts updated successfully!")
        else:
            st.error(f"Error updating prompts: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def send_chat_message(query, email_id=None):
    try:
        response = requests.post(
            f"{API_URL}/agent/chat",
            json={"query": query, "email_id": email_id}
        )
        if response.status_code == 200:
            return response.json()['response']
        return "Error processing your request"
    except Exception as e:
        return f"Error: {str(e)}"

def get_drafts():
    try:
        response = requests.get(f"{API_URL}/drafts")
        if response.status_code == 200:
            return response.json()['drafts']
        return []
    except Exception as e:
        st.error(f"Error fetching drafts: {str(e)}")
        return []

def generate_draft(email_id, instructions=""):
    try:
        response = requests.post(
            f"{API_URL}/drafts/generate",
            json={"email_id": email_id, "instructions": instructions}
        )
        if response.status_code == 201:
            st.success("Draft generated successfully!")
            return response.json()['draft']
        else:
            st.error(f"Error generating draft: {response.json().get('error', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def delete_draft(draft_id):
    try:
        response = requests.delete(f"{API_URL}/drafts/{draft_id}")
        if response.status_code == 200:
            st.success("Draft deleted!")
            st.rerun()
    except Exception as e:
        st.error(f"Error: {str(e)}")

def get_category_color(category):
    """Get color for category badge"""
    colors = {
        'Important': '🔴',
        'Newsletter': '🔵',
        'Spam': '⚫',
        'To-Do': '🟡'
    }
    return colors.get(category, '⚪')

# Header
st.title("📧 Email Productivity Agent")
st.markdown("AI-powered email management and automation")

# Sidebar
with st.sidebar:
    st.header("Controls")
    
    if st.button("oad Mock Inbox", use_container_width=True):
        load_inbox()
    
    if st.button("Process All Emails", use_container_width=True):
        process_emails()
    
    st.divider()
    
    emails = get_emails()
    st.metric("Total Emails", len(emails))
    
    processed = len([e for e in emails if e.get('category')])
    st.metric("Processed", processed)
    
    important = len([e for e in emails if e.get('category') == 'Important'])
    st.metric("Important", important)

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Inbox",
    "Email Agent",
    "Drafts",
    "Prompt Configuration"
])

# Tab 1: Inbox
with tab1:
    emails = get_emails()
    
    if not emails:
        st.info("No emails in inbox. Click 'Load Mock Inbox' to get started.")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Email List")
            
            for email in emails:
                with st.container():
                    # Check if this email is selected
                    is_selected = (st.session_state.selected_email and 
                                 st.session_state.selected_email['id'] == email['id'])
                    
                    button_type = "primary" if is_selected else "secondary"
                    
                    if st.button(
                        f"{' ' if is_selected else ''}{email['sender'][:30]}\n{email['subject'][:40]}",
                        key=f"email_{email['id']}",
                        use_container_width=True,
                        type=button_type
                    ):
                        st.session_state.selected_email = email
                        # Clear chat when selecting new email
                        if st.session_state.last_selected_email_id != email['id']:
                            st.session_state.chat_messages = []
                            st.session_state.last_selected_email_id = email['id']
                        st.rerun()
                    
                    col_a, col_b = st.columns([3, 2])
                    with col_a:
                        st.caption(datetime.fromisoformat(email['timestamp']).strftime("%b %d, %I:%M %p"))
                    with col_b:
                        if email.get('category'):
                            st.caption(f"{get_category_color(email['category'])} {email['category']}")
                    
                    if email.get('action_items'):
                        st.caption(f" {len(email['action_items'])} task(s)")
                    
                    st.divider()
        
        with col2:
            st.subheader("📧 Email Details")
            
            if st.session_state.selected_email:
                email = st.session_state.selected_email
                
                st.markdown(f"**From:** {email['sender']}")
                st.markdown(f"**Subject:** {email['subject']}")
                st.markdown(f"**Date:** {datetime.fromisoformat(email['timestamp']).strftime('%B %d, %Y at %I:%M %p')}")
                
                if email.get('category'):
                    st.markdown(f"**Category:** {get_category_color(email['category'])} {email['category']}")
                
                st.divider()
                
                st.markdown("**Message:**")
                st.write(email['body'])
                
                if email.get('action_items') and len(email['action_items']) > 0:
                    st.divider()
                    st.markdown("**Action Items:**")
                    for item in email['action_items']:
                        st.markdown(f"- {item.get('task', 'Unknown task')}")
                        if item.get('deadline'):
                            st.caption(f"   Deadline: {item['deadline']}")
            else:
                st.info("Select an email from the list to view details")

# Tab 2: Email Agent
with tab2:
    st.subheader("Chat with Email Agent")
    
    # Show currently selected email
    if st.session_state.selected_email:
        st.info(f"Chatting about: **{st.session_state.selected_email['subject']}**")
    else:
        st.warning("No email selected. Select an email from the Inbox tab for context-aware responses.")
    
    # Clear chat button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
    
    # Chat history
    chat_container = st.container()
    with chat_container:
        if len(st.session_state.chat_messages) == 0:
            st.markdown("""
            **Try asking:**
            - "Draft a reply to this email"
            - "Summarize this email"
            - "What are my urgent emails?"
            - "List all my tasks"
            """)
        else:
            for msg in st.session_state.chat_messages:
                if msg['role'] == 'user':
                    st.chat_message("user").write(msg['content'])
                else:
                    st.chat_message("assistant").write(msg['content'])
    
    # Chat input
    user_input = st.chat_input("Ask about your emails...")
    
    if user_input:
        # Add user message
        st.session_state.chat_messages.append({
            'role': 'user',
            'content': user_input
        })
        
        # Get response
        email_id = st.session_state.selected_email['id'] if st.session_state.selected_email else None
        response = send_chat_message(user_input, email_id)
        
        # Add assistant message
        st.session_state.chat_messages.append({
            'role': 'assistant',
            'content': response
        })
        
        st.rerun()
    
    # Quick actions
    st.divider()
    st.markdown("**⚡ Quick Actions:**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Urgent Emails", use_container_width=True):
            response = send_chat_message("What are my urgent emails?")
            st.session_state.chat_messages.append({'role': 'user', 'content': "What are my urgent emails?"})
            st.session_state.chat_messages.append({'role': 'assistant', 'content': response})
            st.rerun()
    
    with col2:
        if st.button("All Tasks", use_container_width=True):
            response = send_chat_message("What tasks do I need to do?")
            st.session_state.chat_messages.append({'role': 'user', 'content': "What tasks do I need to do?"})
            st.session_state.chat_messages.append({'role': 'assistant', 'content': response})
            st.rerun()
    
    with col3:
        if st.button("Summarize", use_container_width=True, disabled=not st.session_state.selected_email):
            if st.session_state.selected_email:
                response = send_chat_message("Summarize this email", st.session_state.selected_email['id'])
                st.session_state.chat_messages.append({'role': 'user', 'content': "Summarize this email"})
                st.session_state.chat_messages.append({'role': 'assistant', 'content': response})
                st.rerun()
    
    with col4:
        if st.button("Draft Reply", use_container_width=True, disabled=not st.session_state.selected_email):
            if st.session_state.selected_email:
                response = send_chat_message("Draft a reply to this email", st.session_state.selected_email['id'])
                st.session_state.chat_messages.append({'role': 'user', 'content': "Draft a reply to this email"})
                st.session_state.chat_messages.append({'role': 'assistant', 'content': response})
                st.rerun()

# Tab 3: Drafts
with tab3:
    st.subheader("Email Drafts")
    
    drafts = get_drafts()
    
    if not drafts:
        st.info("No drafts yet. Generate drafts using the Email Agent.")
        
        if st.session_state.selected_email:
            st.divider()
            st.markdown("**Generate Draft for Selected Email**")
            st.info(f"Selected: {st.session_state.selected_email['subject']}")
            
            instructions = st.text_area(
                "Additional instructions (optional)",
                placeholder="E.g., Keep it formal, mention availability next week..."
            )
            
            if st.button("Generate Draft", use_container_width=True):
                draft = generate_draft(
                    st.session_state.selected_email['id'],
                    instructions
                )
                if draft:
                    st.rerun()
    else:
        for draft in drafts:
            with st.expander(f"{draft['subject']}", expanded=True):
                st.text_input("Subject", draft['subject'], key=f"subj_{draft['id']}")
                st.text_area("Body", draft['body'], height=200, key=f"body_{draft['id']}")
                st.caption(f"Created: {datetime.fromisoformat(draft['created_at']).strftime('%B %d, %Y at %I:%M %p')}")
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("Delete", key=f"del_{draft['id']}"):
                        delete_draft(draft['id'])

# Tab 4: Prompt Configuration
with tab4:
    st.subheader("Prompt Configuration")
    st.markdown("Configure how the AI processes your emails")
    
    prompts = get_prompts()
    
    if prompts:
        with st.form("prompt_form"):
            categorization = st.text_area(
                "Categorization Prompt",
                prompts.get('categorization', ''),
                height=100,
                help="Defines how emails are categorized"
            )
            
            action_item = st.text_area(
                "Action Item Extraction Prompt",
                prompts.get('action_item', ''),
                height=100,
                help="Defines how tasks are extracted from emails"
            )
            
            auto_reply = st.text_area(
                "Auto-Reply Draft Prompt",
                prompts.get('auto_reply', ''),
                height=100,
                help="Defines how reply drafts are generated"
            )
            
            submitted = st.form_submit_button("💾 Save Prompts", use_container_width=True)
            
            if submitted:
                update_prompts({
                    'categorization': categorization,
                    'action_item': action_item,
                    'auto_reply': auto_reply
                })
    else:
        st.warning("No prompts found. Please ensure the backend is running.")

# Footer
st.divider()
st.caption("Email Productivity Agent - AI-Powered Email Management")