from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')  # Use App Password for Gmail

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-email', methods=['POST'])
def generate_email():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        receiver_email = data.get('receiver_email')
        
        if not prompt or not receiver_email:
            return jsonify({'error': 'Prompt and receiver email are required'}), 400
        
        # Generate email content using Gemini
        enhanced_prompt = f"""
        Please draft a professional email based on the following request:
        {prompt}
        
        Please provide:
        1. A clear and appropriate subject line
        2. A well-structured email body with proper greeting and closing
        3. Professional tone and language
        
        Format your response as:
        Subject: [subject line]
        Body: [email body]
        """
        
        response = model.generate_content(enhanced_prompt)
        generated_content = response.text
        
        # Parse subject and body
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
            'receiver_email': receiver_email
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