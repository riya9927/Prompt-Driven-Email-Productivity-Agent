import os
import json
import re


class LLMService:
    
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key or api_key == 'your_api_key_here':
            print("WARNING: ANTHROPIC_API_KEY not set. Using mock responses.")
            print("   Set your API key in .env file to use real AI responses.")
            self.client = None
        else:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=api_key)
                print("Anthropic API initialized successfully")
            except Exception as e:
                print(f"WARNING: Failed to initialize Anthropic API: {e}")
                print("   Falling back to mock responses.")
                self.client = None
        
        self.model = "claude-sonnet-4-20250514"
        self.max_tokens = 1000
    
    def _call_llm(self, prompt, system_prompt=""):
        if not self.client:
            # Return mock responses for testing without API key
            return self._mock_response(prompt, system_prompt)
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt if system_prompt else "You are a helpful email assistant.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"LLM API Error: {e}")
            print("   Falling back to mock response")
            return self._mock_response(prompt, system_prompt)
    
    def _mock_response(self, prompt, system_prompt=""):
        prompt_lower = prompt.lower()
        
        # Extract email body if present in prompt
        email_body = ""
        if "email body:" in prompt_lower:
            parts = prompt.split("Email body:", 1)
            if len(parts) > 1:
                email_body = parts[1].strip()
        elif "email content:" in prompt_lower:
            parts = prompt.split("Email content:", 1)
            if len(parts) > 1:
                email_body = parts[1].strip()
        
        # CATEGORIZATION
        if 'categorize' in prompt_lower and ('email content:' in prompt_lower or 'email body:' in prompt_lower):
            content = email_body or prompt
            if any(word in content.lower() for word in ['urgent', 'asap', 'action required', 'critical']):
                return 'Important'
            elif any(word in content.lower() for word in ['newsletter', 'digest', 'weekly', 'news']):
                return 'Newsletter'
            elif any(word in content.lower() for word in ['limited time', '90%', 'click here now', 'buy now', 'offer', 'discount']):
                return 'Spam'
            elif any(word in content.lower() for word in ['please submit', 'need to', 'must complete', 'required', 'rsvp', 'please']):
                return 'To-Do'
            return 'Important'
        
        # ACTION ITEM EXTRACTION
        elif ('extract task' in prompt_lower or 'action item' in prompt_lower) and 'email body:' in prompt_lower:
            tasks = []
            content = email_body or prompt
            
            if 'submit' in content.lower():
                if 'timesheet' in content.lower():
                    tasks.append({"task": "Submit timesheet", "deadline": "EOD tomorrow"})
                elif 'expense' in content.lower():
                    tasks.append({"task": "Submit expense report", "deadline": "End of week"})
                else:
                    tasks.append({"task": "Submit required document", "deadline": "ASAP"})
            
            if 'schedule' in content.lower() or 'meeting' in content.lower():
                if 'availability' in content.lower():
                    tasks.append({"task": "Share availability for meeting", "deadline": "This week"})
                else:
                    tasks.append({"task": "Schedule meeting", "deadline": "ASAP"})
            
            if 'review' in content.lower():
                if 'annual' in content.lower() or 'performance' in content.lower():
                    tasks.append({"task": "Complete annual self-review", "deadline": "December 1st"})
                elif 'report' in content.lower():
                    tasks.append({"task": "Review progress report", "deadline": "End of week"})
                else:
                    tasks.append({"task": "Review document", "deadline": "End of week"})
            
            if 'complete' in content.lower() and 'training' in content.lower():
                tasks.append({"task": "Complete security training", "deadline": "November 30th"})
            
            if 'rsvp' in content.lower():
                tasks.append({"task": "RSVP for event", "deadline": "Thursday"})
            
            if 'approve' in content.lower() or 'approval' in content.lower():
                tasks.append({"task": "Approve request", "deadline": "End of week"})
            
            return json.dumps(tasks) if tasks else "[]"
        
        elif 'draft' in prompt_lower or 'reply' in prompt_lower:
            # Extract the actual user instruction from the full prompt
            user_instruction = ""
            if "please draft a professional reply" in prompt_lower:
                if "additional instructions:" in prompt_lower:
                    parts = prompt.split("Additional instructions:", 1)
                    if len(parts) > 1:
                        user_instruction = parts[1].strip().lower()
            else:
                # Direct user query
                user_instruction = prompt_lower
            
            # Analyze the email content
            content = email_body or prompt
            content_lower = content.lower()
            
            # Check user's specific instructions first
            if 'formal' in user_instruction and 'agenda' in user_instruction:
                return ("Thank you for reaching out. I am very interested in this opportunity. "
                       "To ensure our discussion is productive, could you please share a detailed agenda "
                       "and any relevant materials in advance? I look forward to our conversation.")
            
            elif 'casual' in user_instruction and 'attend' in user_instruction:
                return "Thanks! I'd love to join. Count me in! Looking forward to it."
            
            elif 'professional' in user_instruction and ('submit' in user_instruction or 'today' in user_instruction):
                return ("Thank you for the reminder. I will submit it by end of day today. "
                       "Everything is ready for review.")
            
            elif 'decline' in user_instruction or 'cannot' in user_instruction:
                return ("Thank you for reaching out. Unfortunately, I won't be able to participate at this time. "
                       "I appreciate your understanding.")
            
            elif 'accept' in user_instruction or 'availability' in user_instruction:
                return ("Thank you for the invitation. I'm available and would be happy to join. "
                       "Please let me know the preferred time and any materials I should review beforehand.")
            
            elif 'more information' in user_instruction or 'details' in user_instruction:
                return ("Thank you for your message. Could you please provide more details about this? "
                       "Specifically, I'd like to know more about the timeline, requirements, and expected outcomes.")
            
            elif 'meeting' in content_lower and 'demo' in content_lower:
                return ("Thank you for your interest in a product demonstration. "
                       "I'd be pleased to present our solution to your stakeholders. "
                       "Could you provide some preferred dates and times? Also, it would be helpful to "
                       "understand your specific requirements so I can tailor the demo accordingly.")
            
            elif 'meeting' in content_lower or 'schedule' in content_lower:
                return ("Thank you for the meeting request. I'd be happy to join. "
                       "Could you please share the agenda and any materials we should review beforehand? "
                       "I'm generally available next week - what times work best for your team?")
            
            elif 'timesheet' in content_lower or ('submit' in content_lower and 'payroll' in content_lower):
                return ("Thank you for the reminder. I will submit my timesheet by EOD today. "
                       "All hours have been accurately recorded and are ready for approval.")
            
            elif 'review' in content_lower and 'annual' in content_lower:
                return ("Thank you for the reminder about the annual review. "
                       "I will complete the self-assessment form in the HR portal by the deadline "
                       "and reach out to schedule our discussion.")
            
            elif 'lunch' in content_lower or 'rsvp' in content_lower:
                return ("Thank you for organizing this! I'd love to join. "
                       "Please count me in. Looking forward to it!")
            
            elif 'expense' in content_lower or 'approval' in content_lower:
                return ("I've reviewed the expense report. Everything looks good. "
                       "Approved - please proceed with processing.")
            
            elif 'training' in content_lower:
                return ("Thank you for the reminder about the training. "
                       "I will complete the module by the deadline. "
                       "Please let me know if there are any specific areas I should focus on.")
            
            elif 'support' in content_lower or 'ticket' in content_lower:
                return ("Thank you for the update. I've verified that the issue is resolved. "
                       "Everything is working as expected now. I appreciate your quick response.")
            
            else:
                return ("Thank you for your email. I've received your message and will review it carefully. "
                       "I'll get back to you with a detailed response shortly.")
        
        elif 'summarize' in prompt_lower or 'summary' in prompt_lower:
            content = email_body or prompt
            subject = ""
            if "subject:" in content.lower():
                lines = content.split('\n')
                for line in lines:
                    if 'subject:' in line.lower():
                        subject = line.split(':', 1)[1].strip()
                        break
            
            if 'meeting' in content.lower():
                return f"This email is a meeting request. The sender wants to schedule a discussion and is asking for your availability."
            elif 'urgent' in content.lower() or 'asap' in content.lower():
                return f"This is an urgent email requiring immediate attention. Action is needed as soon as possible."
            elif 'submit' in content.lower():
                return f"This email requests submission of documents or information by a specific deadline."
            else:
                return f"This email contains information that may require your attention or response."
        
        else:
            return "I understand your request and will help you with that. Could you please provide more specific details about what you'd like me to do?"
    
    def categorize_email(self, email_content, categorization_prompt):
        prompt = f"""{categorization_prompt}

Email content:
{email_content}

Please respond with only the category name: Important, Newsletter, Spam, or To-Do."""
        
        response = self._call_llm(prompt, system_prompt="You are an email categorization assistant.")
        response = response.strip()
        valid_categories = ['Important', 'Newsletter', 'Spam', 'To-Do']
        
        for cat in valid_categories:
            if cat.lower() in response.lower():
                return cat
        
        return 'Important'  
    
    def extract_action_items(self, email_body, action_item_prompt):
        prompt = f"""{action_item_prompt}

Email body:
{email_body}

Please respond with a JSON array of tasks, or an empty array [] if no tasks found."""
        
        response = self._call_llm(prompt, system_prompt="You are an action item extraction assistant.")
        
        # Try to parse JSON from response
        try:
            response = response.strip()
            if response.startswith('```'):
                match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response, re.DOTALL)
                if match:
                    response = match.group(1)
                else:
                    # Try to find JSON array without proper fencing
                    response = response.replace('```json', '').replace('```', '').strip()
            
            tasks = json.loads(response)
            
            if isinstance(tasks, list):
                return tasks
            return []
        except json.JSONDecodeError as e:
            print(f"Failed to parse action items JSON: {e}")
            print(f"Response was: {response[:100]}...")
            return []
    
    def generate_reply(self, email_body, auto_reply_prompt, custom_instructions=""):
        prompt = f"""{auto_reply_prompt}

Email body:
{email_body}

{f"Additional instructions: {custom_instructions}" if custom_instructions else ""}

Please draft a professional reply."""
        
        response = self._call_llm(prompt, system_prompt="You are a professional email writing assistant.")
        return response.strip()
    
    def process_chat_query(self, query, context, prompts):
        query_lower = query.lower()
        
        # Summarize email
        if 'summarize' in query_lower and context.get('email'):
            email = context['email']
            prompt = f"""Please provide a brief summary of this email:

From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}

Provide a 2-3 sentence summary highlighting the key points and any actions needed."""
            
            return self._call_llm(prompt, system_prompt="You are an email summarization assistant.")
        
        # Find urgent/important emails
        elif 'urgent' in query_lower or 'important' in query_lower:
            emails = context.get('all_emails', [])
            urgent = [e for e in emails if e.get('category') == 'Important']
            
            if urgent:
                subjects = [e['subject'] for e in urgent[:5]]
                if len(urgent) > 5:
                    return f"You have {len(urgent)} urgent emails. Here are the most recent:\n" + "\n".join(f"• {s}" for s in subjects) + f"\n...and {len(urgent) - 5} more."
                else:
                    return f"You have {len(urgent)} urgent email(s):\n" + "\n".join(f"• {s}" for s in subjects)
            return "You have no urgent emails at the moment. Great job staying on top of things!"
        
        # List tasks/to-dos
        elif 'task' in query_lower or 'to-do' in query_lower or 'action' in query_lower:
            emails = context.get('all_emails', [])
            all_tasks = []
            
            for email in emails:
                if email.get('action_items'):
                    for item in email['action_items']:
                        all_tasks.append({
                            'task': item.get('task', 'Unknown task'),
                            'deadline': item.get('deadline', 'No deadline'),
                            'from': email['sender']
                        })
            
            if all_tasks:
                task_list = []
                for i, t in enumerate(all_tasks[:10], 1):
                    deadline_str = f" (Due: {t['deadline']})" if t['deadline'] != 'No deadline' else ""
                    task_list.append(f"{i}. {t['task']}{deadline_str} - from {t['from']}")
                
                response = f"Here are your pending tasks:\n\n" + "\n".join(task_list)
                if len(all_tasks) > 10:
                    response += f"\n\n...and {len(all_tasks) - 10} more tasks."
                return response
            return "You have no pending tasks in your emails. Your inbox is all caught up!"
        
        elif 'draft' in query_lower and context.get('email'):
            email = context['email']
            draft = self.generate_reply(email['body'], prompts.get('auto_reply', ''), query)
            return f"Here's a draft reply:\n\n{draft}\n\n---\nYou can edit this draft in the Drafts tab before sending."
        
        elif 'from' in query_lower or 'sender' in query_lower:
            emails = context.get('all_emails', [])
            words = query.split()
            potential_sender = None
            for i, word in enumerate(words):
                if word.lower() == 'from' and i + 1 < len(words):
                    potential_sender = words[i + 1].strip('?.,!')
                    break
            
            if potential_sender:
                matching = [e for e in emails if potential_sender.lower() in e['sender'].lower()]
                if matching:
                    subjects = [f"• {e['subject']}" for e in matching[:5]]
                    return f"Found {len(matching)} email(s) from {potential_sender}:\n" + "\n".join(subjects)
                return f"No emails found from {potential_sender}."
        
        else:
            emails = context.get('all_emails', [])
            email_summaries = "\n".join([
                f"- From {e['sender']}: {e['subject']} (Category: {e.get('category', 'Uncategorized')})"
                for e in emails[:10]
            ])
            
            prompt = f"""You are an email assistant. The user has asked: "{query}"

Here are the most recent emails in their inbox:
{email_summaries}

Please provide a helpful, concise response to their query."""
            
            return self._call_llm(prompt, system_prompt="You are a helpful email management assistant.")


if __name__ == '__main__':    
    llm_service = LLMService()
    
    test_queries = [
        "Draft a formal reply expressing interest and requesting an agenda",
        "Draft a casual reply saying I'll attend",
        "Draft a professional reply confirming I'll submit it today",
        "Draft a reply declining politely",
        "Draft a reply asking for more information"
    ]
    
    test_email = "Can we schedule a meeting next week to discuss the project?"
    
    print("Testing different draft requests:\n")
    for query in test_queries:
        print(f"Query: {query}")
        response = llm_service.generate_reply(test_email, "Draft a professional reply", query)
        print(f"Response: {response}\n")
    