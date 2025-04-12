# Project Management Chatbot

<div align="center">
  <img src="staticfiles\admin\img\pm_chatbot.png" alt="PM Chatbot Logo" width="100" height="100">
  <h3>Intelligent Project Data Assistant</h3>
  <p>Your AI-powered companion for project insights</p>
</div>

## 📋 Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [User Guide](#user-guide)
  - [Getting Started](#getting-started)
  - [Using the Chat Interface](#using-the-chat-interface)
  - [Model Selection](#model-selection)
  - [Chat Sessions](#chat-sessions)
  - [Dashboard and Analytics](#dashboard-and-analytics)
  - [Sample Questions](#sample-questions)
- [Technical Setup](#technical-setup)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Admin Guide](#admin-guide)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [Production Deployment](#production-deployment)
- [License](#license)

## 🔍 Overview

The Project Management Chatbot is an intelligent assistant that connects to your Google Sheets project database and provides natural language answers to your questions. Simply type your questions about projects, budgets, timelines, or team members, and get instant insights powered by OpenAI and Google Gemini AI models.

This application brings your project data to life, allowing both technical and non-technical team members to access critical information through a simple conversation interface. No SQL queries or spreadsheet formulas needed!

## ✨ Key Features

- **Google Sheets Integration**: Connect directly to your existing project data in Google Sheets
- **Dual AI Models**: Choose between two powerful AI engines:
  - **Google Gemini**: Google's latest AI model for fast, efficient responses
  - **OpenAI**: Access OpenAI's powerful language models for rich, detailed answers
- **Natural Language Interface**: Ask questions in plain English about projects, budgets, timelines, resources
- **Real-time Responses**: Get immediate answers through our WebSocket technology
- **Multi-Sheet Support**: Query across multiple project sheets (Marketing, Development, etc.)
- **Chat History**: Save all conversations for future reference and knowledge sharing
- **Session Management**: Create multiple chat sessions for different topics or projects
- **Usage Analytics**: Track usage patterns and most frequent questions
- **Budget Analysis**: Automatically identify over-budget or under-budget projects
- **Responsive Design**: Works on desktops, tablets, and mobile devices
- **Fallback Strategy**: Seamlessly switches between AI models if one experiences issues

## 📱 User Guide

### Getting Started

1. **Access**: Navigate to the application URL provided by your administrator
2. **Login**: Use your provided username and password to log in
3. **Registration**: If you're a new user, click "Register" to create an account (if enabled)

### Using the Chat Interface

The chat interface is designed to be intuitive and similar to popular messaging apps:

1. **Ask Questions**: Type your project-related questions in the text box at the bottom
2. **View Responses**: The AI will respond within seconds, showing its answers in the chat window
3. **Star Important Messages**: Click the star icon next to any response to mark it as important
4. **Refresh Data**: Click the refresh icon to get the latest data from Google Sheets before asking a question
5. **Continue Conversations**: The AI remembers your previous questions within a session, so you can ask follow-up questions

### Model Selection

You can switch between AI models based on your preference:

1. Use the model selector toggle at the top of the chat interface
2. Choose "OpenAI" or "Gemini" based on which gives better responses for your specific questions
3. The system will remember your preference for future sessions

### Chat Sessions

Organize your conversations by topic or project:

1. **Create New Session**: Click "New Chat" to start a fresh conversation
2. **Switch Sessions**: Use the dropdown to view and switch between different chat sessions
3. **Rename Sessions**: Click the pencil icon next to a session name to rename it
4. **Delete Sessions**: Remove unwanted sessions using the trash icon

### Dashboard and Analytics

Access insights about your chatbot usage:

1. Navigate to the Dashboard tab to see usage statistics
2. View charts showing message frequency, model usage, and most active sessions
3. Get insights into which projects are being discussed most frequently

### Sample Questions

Here are some examples of questions you can ask the chatbot:

#### Project Status
- "Show me all active projects"
- "What's the current status of the Website Redesign project?"
- "Which projects are scheduled to finish this month?"
- "How many projects are currently on hold?"

#### Budget Queries
- "Which projects are currently over budget?"
- "What's the remaining budget for the Marketing Campaign project?"
- "Show me the top 5 projects by budget size"
- "Calculate the total budget across all active projects"

#### Timeline and Schedule
- "When is the Mobile App project scheduled to complete?"
- "Which projects have deadlines within the next 30 days?"
- "Show me projects that started in January"
- "Has the Cloud Migration project deadline been extended?"

#### Team and Resources
- "Who is working on the E-commerce Platform project?"
- "Show me all team members with the role 'Developer'"
- "Which projects does Jane Smith work on?"
- "How many team members are assigned to the CRM Integration project?"

#### Cross-Sheet Analysis
- "Compare the budgets between Marketing and Development projects"
- "Which department has the most active projects?"
- "Show me all projects related to website development across all departments"

## 🛠️ Technical Setup

### Requirements

- Python 3.9+
- Django 5.0+
- Django Channels 4.0+ (for WebSockets)
- OpenAI API key
- Google Gemini API key
- Google Sheets API credentials

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pm_chatbot.git
   cd pm_chatbot
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Configuration

1. Create a `.env` file in the project root with the following variables:
   ```
   # Django settings
   DJANGO_SECRET_KEY=your_django_secret_key_here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # API keys
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here

   # Google Sheets configuration
   GOOGLE_SHEETS_CREDENTIALS_FILE=path_to_your_google_sheets_credentials.json
   GOOGLE_SHEETS_PROJECT_DB=your_google_sheets_id_here
   
   # Optional: Additional sheets in format "name1:id1,name2:id2"
   ADDITIONAL_SHEETS=Marketing:sheet_id_1,Development:sheet_id_2
   ```

2. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

3. Create an admin user:
   ```
   python manage.py create_admin --username admin --password adminpassword --email admin@example.com
   ```

4. Start the server with WebSocket support (recommended):
   ```
   daphne project_chatbot.asgi:application -p 8000
   ```
   
   Alternatively, use the Django development server (limited WebSocket support):
   ```
   python manage.py runserver
   ```

5. Access the application at http://localhost:8000

## 👩‍💼 Admin Guide

As an administrator, you have additional capabilities:

1. **User Management**: Access the Django admin panel (/admin) to manage user accounts
2. **System Monitoring**: View system logs and monitor API usage
3. **Database Management**: Directly access and update the Google Sheets connection
4. **Analytics Access**: View detailed analytics about system usage
5. **Custom Setup**: Configure additional sheets and data connections

## 🔧 Advanced Features

### Real-time Chat with WebSockets
The application uses Django Channels and WebSockets to provide real-time chat functionality:
- Instant responses without page reloads
- Typing indicators when the AI is processing
- Connection resilience with automatic fallback to AJAX

### Model Switching
Dynamically switch between AI models:
- Google Gemini 1.5-Flash: Fast and efficient for most queries
- OpenAI GPT-4o-mini: Excellent for complex analytical questions

### Dashboard Analytics
Track and analyze your chatbot usage:
- Message frequency over time
- Model distribution and usage statistics
- Most active chat sessions

### Chat Session Management
- Create multiple chat sessions for different topics
- Switch between sessions seamlessly
- View, export, and delete past sessions

## ❓ Troubleshooting

**Q: The chatbot doesn't understand my question**  
A: Try rephrasing your question to be more specific. Include project names, dates, or specific terms that match your Google Sheets data.

**Q: I'm seeing an error about API limits**  
A: This happens when you've reached the usage limits for the AI models. Wait a few minutes before trying again or switch to the other model.

**Q: The data seems outdated**  
A: Click the refresh icon before asking your question to get the latest data from Google Sheets.

**Q: The chatbot is slow to respond**  
A: Complex questions analyzing large datasets may take longer. Try splitting your question into smaller parts.

**Q: I lost my chat history**  
A: Chat sessions are saved per user. Make sure you're logged in with the correct account and check the session dropdown.

## 🔒 Security

The application implements standard Django security practices:
- CSRF protection for all forms
- WebSocket authentication
- XSS protection
- Content-Type sniffing prevention
- X-Frame-Options set to DENY
- Google Sheets API used with limited-scope credentials

## 🚀 Production Deployment

For production deployment, we recommend:
1. Using Daphne or Uvicorn behind a reverse proxy like Nginx
2. Enabling HTTPS for secure WebSocket connections (WSS)
3. Setting up Redis as the channel layer backend
4. Configuring proper database backends (PostgreSQL recommended)
5. Implementing regular backups of the database
6. Setting up monitoring for API usage and system performance


---

<div align="center">
  <p>Developed with ❤️ by Avishek Paul</p>
  <p>© 2025 All Rights Reserved</p>
</div>
