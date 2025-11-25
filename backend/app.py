from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from services.email_service import EmailService
from services.llm_service import LLMService
from services.prompt_service import PromptService
from models.database import Database

app = Flask(__name__)
CORS(app)

# Initialize services
db = Database()
email_service = EmailService(db)
llm_service = LLMService()
prompt_service = PromptService(db)

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Email endpoints
@app.route('/api/emails', methods=['GET'])
def get_emails():
    try:
        emails = email_service.get_all_emails()
        return jsonify({"emails": emails}), 200
    except Exception as e:
        print(f"Error in get_emails: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/emails/<int:email_id>', methods=['GET'])
def get_email(email_id):
    try:
        email = email_service.get_email_by_id(email_id)
        if email:
            return jsonify(email), 200
        return jsonify({"error": "Email not found"}), 404
    except Exception as e:
        print(f"Error in get_email: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/emails/load', methods=['POST'])
def load_inbox():
    try:
        print("Loading mock inbox...")
        count = email_service.load_mock_inbox()
        print(f"Successfully loaded {count} emails")
        return jsonify({
            "message": f"Successfully loaded {count} emails",
            "count": count
        }), 200
    except Exception as e:
        print(f"Error in load_inbox: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/emails/process', methods=['POST'])
def process_emails():
    try:
        data = request.get_json() if request.is_json else {}
        email_ids = data.get('email_ids', None)
        
        if email_ids:
            emails = [email_service.get_email_by_id(eid) for eid in email_ids]
            emails = [e for e in emails if e is not None]
        else:
            emails = email_service.get_all_emails()
        
        # Get prompts
        prompts = prompt_service.get_all_prompts()
        
        results = []
        for email in emails:
            if not email:
                continue
            
            try:
                # Categorize email
                category = llm_service.categorize_email(
                    email['subject'] + " " + email['body'],
                    prompts['categorization']
                )
                
                # Extract action items
                action_items = llm_service.extract_action_items(
                    email['body'],
                    prompts['action_item']
                )
                
                # Update email in database
                email_service.update_email(
                    email['id'],
                    category=category,
                    action_items=action_items
                )
                
                results.append({
                    "email_id": email['id'],
                    "category": category,
                    "action_items": action_items
                })
            except Exception as e:
                print(f"Error processing email {email['id']}: {e}")
                continue
        
        return jsonify({
            "message": "Emails processed successfully",
            "results": results
        }), 200
    except Exception as e:
        print(f"Error in process_emails: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Prompt endpoints
@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    try:
        prompts = prompt_service.get_all_prompts()
        return jsonify(prompts), 200
    except Exception as e:
        print(f"Error in get_prompts: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompts', methods=['PUT'])
def update_prompts():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        prompt_service.update_prompts(data)
        return jsonify({"message": "Prompts updated successfully"}), 200
    except Exception as e:
        print(f"Error in update_prompts: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompts/<prompt_type>', methods=['GET'])
def get_prompt(prompt_type):
    try:
        prompt = prompt_service.get_prompt(prompt_type)
        return jsonify({"prompt": prompt}), 200
    except Exception as e:
        print(f"Error in get_prompt: {e}")
        return jsonify({"error": str(e)}), 500

# Chat/Agent endpoints
@app.route('/api/agent/chat', methods=['POST'])
def agent_chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        query = data.get('query', '')
        email_id = data.get('email_id', None)
        
        # Get context
        context = {}
        if email_id:
            email = email_service.get_email_by_id(email_id)
            context['email'] = email
        
        # Get all emails for general queries
        context['all_emails'] = email_service.get_all_emails()
        
        # Get prompts
        prompts = prompt_service.get_all_prompts()
        
        # Process query with LLM
        response = llm_service.process_chat_query(query, context, prompts)
        
        return jsonify({
            "response": response,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        print(f"Error in agent_chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Draft endpoints
@app.route('/api/drafts', methods=['GET'])
def get_drafts():
    try:
        drafts = email_service.get_all_drafts()
        return jsonify({"drafts": drafts}), 200
    except Exception as e:
        print(f"Error in get_drafts: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/drafts', methods=['POST'])
def create_draft():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        draft_id = email_service.create_draft(
            email_id=data.get('email_id'),
            subject=data.get('subject'),
            body=data.get('body'),
            metadata=data.get('metadata', {})
        )
        return jsonify({
            "message": "Draft created successfully",
            "draft_id": draft_id
        }), 201
    except Exception as e:
        print(f"Error in create_draft: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/drafts/<int:draft_id>', methods=['PUT'])
def update_draft(draft_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email_service.update_draft(
            draft_id,
            subject=data.get('subject'),
            body=data.get('body'),
            metadata=data.get('metadata')
        )
        return jsonify({"message": "Draft updated successfully"}), 200
    except Exception as e:
        print(f"Error in update_draft: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/drafts/<int:draft_id>', methods=['DELETE'])
def delete_draft(draft_id):
    try:
        email_service.delete_draft(draft_id)
        return jsonify({"message": "Draft deleted successfully"}), 200
    except Exception as e:
        print(f"Error in delete_draft: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/drafts/generate', methods=['POST'])
def generate_draft():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email_id = data.get('email_id')
        custom_instructions = data.get('instructions', '')
        
        # Get email
        email = email_service.get_email_by_id(email_id)
        if not email:
            return jsonify({"error": "Email not found"}), 404
        
        # Get auto-reply prompt
        prompts = prompt_service.get_all_prompts()
        
        # Generate draft
        draft_body = llm_service.generate_reply(
            email['body'],
            prompts['auto_reply'],
            custom_instructions
        )
        
        # Create draft
        draft_id = email_service.create_draft(
            email_id=email_id,
            subject=f"Re: {email['subject']}",
            body=draft_body,
            metadata={"generated": True}
        )
        
        return jsonify({
            "message": "Draft generated successfully",
            "draft_id": draft_id,
            "draft": {
                "subject": f"Re: {email['subject']}",
                "body": draft_body
            }
        }), 201
    except Exception as e:
        print(f"Error in generate_draft: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Initializing database...")
    db.initialize()
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)