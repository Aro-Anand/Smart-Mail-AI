
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import json
import re
from dotenv import load_dotenv
from prompts import DEFAULT_EMAIL_AGENT_PROMPT

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    generation_config=genai.types.GenerationConfig(
        temperature=0.3,
        top_p=0.8,
        top_k=40,
        max_output_tokens=1024,
    )
)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')

def extract_name_from_email(email):
    if not email or '@' not in email:
        return None
    username = email.split('@')[0]
    name_part = re.sub(r'[0-9]+', '', username)
    name_part = re.sub(r'[._-]', ' ', name_part)
    name_parts = name_part.split()
    if name_parts:
        return ' '.join(word.capitalize() for word in name_parts if word)
    return None

def get_email_prompt(user_request, recipient_email, recipient_name=None, tone="professional"):
    name_context = f"\nRecipient Name: {recipient_name}" if recipient_name else ""
    tone_guidance = {
        "professional": "Use a professional, business-appropriate tone.",
        "friendly": "Use a warm, friendly tone.",
        "formal": "Use a very formal, ceremonious tone.",
        "casual": "Use a relaxed, informal tone.",
        "persuasive": "Use a compelling, convincing tone.",
        "apologetic": "Use an apologetic, regretful tone."
    }
    tone_instruction = tone_guidance.get(tone, tone_guidance["professional"])
    return f"""
    {DEFAULT_EMAIL_AGENT_PROMPT}

    User Request: {user_request}
    Recipient Email: {recipient_email}{name_context}
    Tone: {tone.capitalize()} - {tone_instruction}

    Please draft an appropriate email with consistent tone.
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
        tone = data.get('tone', 'professional')

        if not prompt or not receiver_email:
            return jsonify({'error': 'Prompt and receiver email are required'}), 400

        recipient_name = extract_name_from_email(receiver_email)
        enhanced_prompt = get_email_prompt(prompt, receiver_email, recipient_name, tone)
        response = model.generate_content(enhanced_prompt)
        generated_content = response.text

        try:
            json_match = re.search(r'\{.*\}', generated_content, re.DOTALL)
            if json_match:
                email_data = json.loads(json_match.group())
                subject = email_data.get('subject', 'Generated Email')
                body = email_data.get('body', generated_content)
                tone = email_data.get('tone', 'professional')
            else:
                raise ValueError("No JSON found")
        except (json.JSONDecodeError, ValueError):
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
        subject = request.form.get('subject')
        body = request.form.get('body')
        receiver_emails = request.form.get('receiver_emails', '')

        if not all([subject, body, receiver_emails]):
            return jsonify({'error': 'Subject, body, and receiver email(s) are required'}), 400

        attachments = []
        files = request.files.getlist('attachments')
        for file in files:
            if file.filename:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{file.filename}"')
                attachments.append(part)

        recipient_list = [email.strip() for email in receiver_emails.split(',') if email.strip()]
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        for recipient in recipient_list:
            name = extract_name_from_email(recipient)
            lines = body.strip().split('\n')
            if lines and re.match(r'^\s*(Hi|Hello|Dear)\s', lines[0], re.IGNORECASE):
                lines[0] = f"Hi {name},"
            personalized_body = '\n'.join(lines)

            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(personalized_body, 'plain'))

            for part in attachments:
                msg.attach(part)

            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())

        server.quit()
        return jsonify({'message': 'Emails sent individually to each recipient!'})

    except Exception as e:
        return jsonify({'error': f'Error sending email: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
