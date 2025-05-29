from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API with optimal temperature for email drafting
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    generation_config=genai.types.GenerationConfig(
        temperature=0.3,  # Lower temperature for more consistent, professional emails
        top_p=0.8,
        top_k=40,
        max_output_tokens=1024,
    )
)

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')  # Use App Password for Gmail

# Integrated email prompts
DEFAULT_EMAIL_AGENT_PROMPT = """
You are an intelligent email drafting assistant. Your role is to:

1. Analyze user requests and extract key information
2. Draft professional, contextually appropriate emails
3. Maintain proper email etiquette and formatting
4. Adapt tone based on the recipient and purpose

Guidelines:
- Always include appropriate subject lines
- Use professional but friendly tone for business emails
- Be concise yet comprehensive
- Include proper greetings and closings
- Format content with proper paragraphs and structure

When drafting emails:
- Subject: Create a clear, specific subject line
- Greeting: Use appropriate salutation based on context and recipient name
- Body: Structure content logically with clear paragraphs
- Closing: End with professional sign-off
- Signature: Include sender information if provided

Always respond with email content in this JSON format:
{
    "subject": "Email subject here",
    "body": "Email body content here",
    "tone": "professional/casual/formal"
}
"""

def extract_name_from_email(email):
    """Extract a likely name from an email address"""
    if not email or '@' not in email:
        return None
    
    # Get the part before @
    username = email.split('@')[0]
    
    # Common patterns to extract names
    # Remove numbers and common separators
    name_part = re.sub(r'[0-9]+', '', username)
    name_part = re.sub(r'[._-]', ' ', name_part)
    
    # Split and capitalize each part
    name_parts = name_part.split()
    if name_parts:
        # Capitalize each part and join
        formatted_name = ' '.join(word.capitalize() for word in name_parts if word)
        return formatted_name if formatted_name else None
    
    return None

def get_email_prompt(user_request, recipient_email, recipient_name=None, tone="professional"):
    """Generate enhanced email prompt with recipient context and tone"""
    name_context = ""
    if recipient_name:
        name_context = f"\nRecipient Name: {recipient_name}"
    
    tone_guidance = {
        "professional": "Use a professional, business-appropriate tone. Be courteous and respectful.",
        "friendly": "Use a warm, friendly tone while maintaining professionalism. Be approachable and personable.",
        "formal": "Use a very formal, ceremonious tone. Be extremely respectful and traditional in language.",
        "casual": "Use a relaxed, informal tone. Be conversational but still appropriate.",
        "persuasive": "Use a compelling, convincing tone. Be confident and persuasive in your approach.",
        "apologetic": "Use an apologetic, regretful tone. Express sincere apologies and take responsibility."
    }
    
    tone_instruction = tone_guidance.get(tone, tone_guidance["professional"])
    
    return f"""
    {DEFAULT_EMAIL_AGENT_PROMPT}
    
    User Request: {user_request}
    Recipient Email: {recipient_email}{name_context}
    Tone: {tone.capitalize()} - {tone_instruction}
    
    Please draft an appropriate email based on this request with the specified tone. If a recipient name is provided, use it in the greeting. Otherwise, use a generic professional greeting that matches the requested tone.
    
    Ensure the email tone is consistently {tone} throughout the subject line and body.
    """

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-email', methods=['POST'])
def generate_email():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        receiver_email = data.get('receiver_email')
        tone = data.get('tone', 'professional')  # Default to professional tone
        
        if not prompt or not receiver_email:
            return jsonify({'error': 'Prompt and receiver email are required'}), 400
        
        # Extract name from email
        recipient_name = extract_name_from_email(receiver_email)
        
        # Generate email content using enhanced prompt
        enhanced_prompt = get_email_prompt(prompt, receiver_email, recipient_name, tone)
        
        response = model.generate_content(enhanced_prompt)
        generated_content = response.text
        
        # Try to parse JSON response first
        try:
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', generated_content, re.DOTALL)
            if json_match:
                email_data = json.loads(json_match.group())
                subject = email_data.get('subject', 'Generated Email')
                body = email_data.get('body', generated_content)
                tone = email_data.get('tone', 'professional')
            else:
                raise ValueError("No JSON found")
        except (json.JSONDecodeError, ValueError):
            # Fallback to text parsing
            lines = generated_content.split('\n')
            subject = ""
            body = ""
            
            for i, line in enumerate(lines):
                if line.startswith('Subject:'):
                    subject = line.replace('Subject:', '').strip()
                elif line.startswith('Body:'):
                    body = '\n'.join(lines[i+1:]).strip()
                    break
            
            if not subject:
                subject = "Generated Email"
            if not body:
                body = generated_content
            tone = tone  # Use the requested tone
        
        return jsonify({
            'subject': subject,
            'body': body,
            'receiver_email': receiver_email,
            'recipient_name': recipient_name,
            'tone': tone
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating email: {str(e)}'}), 500

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        data = request.get_json()
        subject = data.get('subject')
        body = data.get('body')
        receiver_email = data.get('receiver_email')
        
        if not all([subject, body, receiver_email]):
            return jsonify({'error': 'Subject, body, and receiver email are required'}), 400
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Enable TLS encryption
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, receiver_email, text)
        server.quit()
        
        return jsonify({'message': 'Email sent successfully!'})
        
    except Exception as e:
        return jsonify({'error': f'Error sending email: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)