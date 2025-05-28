# SMART MAIL AI 📧✨

<div align="center">
  <h3>Generate and send professional emails powered by AI</h3>
  <p>
    <a href="#features">Features</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#api-documentation">API</a> •
    <a href="#contributing">Contributing</a>
  </p>
  
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
  [![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com)
  [![Gemini AI](https://img.shields.io/badge/Gemini-AI-orange.svg)](https://ai.google.dev)
</div>

---

## 🎯 Overview

**SMART MAIL AI** is a modern web application that leverages Google's Gemini AI to generate professional emails based on natural language prompts. Simply describe what you want to say, specify the recipient, and let AI craft a polished email that gets sent instantly.

### Why AI Email Composer?

- **⚡ Lightning Fast**: Generate professional emails in seconds
- **🎨 Professional Quality**: AI ensures proper tone and structure
- **📱 Modern Interface**: Beautiful, responsive design that works everywhere
- **🔒 Secure**: Built with security best practices and encrypted connections
- **🚀 Easy to Use**: No complex setup - just describe what you need

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI-Powered Generation** | Uses Google Gemini AI to create contextually appropriate emails |
| 📧 **Direct Email Sending** | Send emails instantly through secure SMTP |
| 👀 **Live Preview** | Review generated content before sending |
| 📱 **Responsive Design** | Works perfectly on desktop, tablet, and mobile |
| ⚡ **Real-time Feedback** | Loading states, success notifications, and error handling |
| 🎨 **Modern UI/UX** | Clean, professional interface with smooth animations |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Gmail account with 2-factor authentication
- Google AI Studio account (for Gemini API)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-email-composer.git
   cd ai-email-composer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_gmail_app_password
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   
   Navigate to `http://localhost:5000`

### Getting API Keys

<details>
<summary><strong>🔑 Gemini API Key Setup</strong></summary>

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new project or select existing one
3. Click "Create API Key"
4. Copy the generated key to your `.env` file

</details>

<details>
<summary><strong>📧 Gmail App Password Setup</strong></summary>

1. Enable 2-Factor Authentication on your Gmail account
2. Go to [Google Account Settings](https://myaccount.google.com)
3. Navigate to **Security** → **2-Step Verification** → **App passwords**
4. Select "Mail" and generate a new app password
5. Use this 16-character password in your `.env` file

</details>

---

## 📖 Usage

### Basic Usage

1. **Enter your prompt**: Describe the email you want to send
   ```
   "Write a professional follow-up email for yesterday's job interview"
   ```

2. **Add recipient email**: Enter the receiver's email address
   ```
   hiring.manager@company.com
   ```

3. **Generate & Preview**: Click "Generate Email" to see the AI-created content

4. **Send**: Review the email and click "Send Email" to deliver it instantly

### Example Prompts

| Prompt | Use Case |
|--------|----------|
| `"Write a thank you email for the business meeting today"` | Professional gratitude |
| `"Compose a follow-up email for my job application"` | Job applications |
| `"Draft an apology email for missing the deadline"` | Professional apologies |
| `"Create a welcome email for new team members"` | Team onboarding |
| `"Write a project update email for stakeholders"` | Status updates |

---

## 🏗️ Project Structure

```
ai-email-composer/
├── app.py                  # Flask backend application
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create this)
├── templates/
│   └── index.html         # Frontend interface
├── static/               # Static assets (if any)
├── README.md             # This file
└── LICENSE               # MIT License
```

---

## 🔧 API Documentation

### Generate Email

**Endpoint:** `POST /generate-email`

```bash
curl -X POST http://localhost:5000/generate-email \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a professional thank you email",
    "receiver_email": "recipient@example.com"
  }'
```

**Response:**
```json
{
  "subject": "Thank You for Your Time",
  "body": "Dear [Name],\n\nI wanted to extend my sincere gratitude...",
  "receiver_email": "recipient@example.com"
}
```

### Send Email

**Endpoint:** `POST /send-email`

```bash
curl -X POST http://localhost:5000/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Thank You for Your Time",
    "body": "Email content here...",
    "receiver_email": "recipient@example.com"
  }'
```

**Response:**
```json
{
  "message": "Email sent successfully!"
}
```

---

## 🛠️ Development

### Setting up Development Environment

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run in development mode**
   ```bash
   export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
   python app.py
   ```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest tests/
```

### Code Style

This project follows PEP 8 style guidelines. Format your code using:

```bash
pip install black flake8
black app.py
flake8 app.py
```

---

## 🚀 Deployment

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t ai-email-composer .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 \
     -e GEMINI_API_KEY=your_key \
     -e SENDER_EMAIL=your_email \
     -e SENDER_PASSWORD=your_password \
     ai-email-composer
   ```

### Production Deployment

For production deployment, consider:

- Use a production WSGI server (Gunicorn, uWSGI)
- Set up reverse proxy (Nginx)
- Enable HTTPS with SSL certificates
- Configure environment variables securely
- Set up monitoring and logging

---

## 🔒 Security

- **Environment Variables**: All sensitive data is stored in environment variables
- **SMTP Security**: Uses TLS encryption for email transmission
- **Input Validation**: All user inputs are validated and sanitized
- **App Passwords**: Uses Gmail app passwords instead of account passwords

### Security Best Practices

- Keep your `.env` file out of version control
- Regularly rotate API keys and passwords
- Use HTTPS in production
- Implement rate limiting for production use

---

## 🐛 Troubleshooting

<details>
<summary><strong>Common Issues</strong></summary>

### "Invalid API Key" Error
- Verify your Gemini API key is correct
- Check if billing is enabled on Google Cloud
- Ensure the API key has proper permissions

### "Email Authentication Failed"
- Confirm 2FA is enabled on Gmail
- Regenerate Gmail app password
- Check email format in `.env` file

### "CORS Error" in Browser
- Ensure Flask-CORS is installed
- Check if backend server is running
- Verify port numbers match

### "Failed to Fetch" Error
- Check if backend is running on correct port
- Verify API endpoint URLs
- Check browser console for detailed errors

</details>

---
