# Project Management Chatbot

## Overview
A Django-based chatbot application that answers questions about projects stored in a database. The chatbot supports dual AI models (Google Gemini and OpenAI GPT) with real-time WebSocket communication.

## Features

- **Project Database**: Access project information from Google Sheets
- **Natural Language Interface**: Ask questions about projects in natural language
- **Dashboard Integration**: View project statistics and analytics
- **Budget Analysis**: Analyze project budgets and identify over/under budget projects
- **Multi-Sheet Support**: Query data across multiple project sheets
- **Real-time Chat**: WebSocket support for immediate responses
- **Dual AI Models**: Switch between Google Gemini and OpenAI models
- **Chat History**: Save, browse, and export conversation history
- **Analytics Dashboard**: Visualize usage patterns and model performance
- **Session Management**: Create and switch between multiple chat sessions

## Requirements

- Python 3.9+
- Django 5.0+
- Django Channels 4.0+ (for WebSockets)
- OpenAI API key
- Google Gemini API key
- Google Sheets API credentials

## Setup Instructions

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

4. Create a `.env` file in the project root with the following variables:
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

5. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create an admin user:
   ```
   python manage.py create_admin --username admin --password adminpassword --email admin@example.com
   ```

7. Start the server with WebSocket support (recommended):
   ```
   daphne project_chatbot.asgi:application -p 8000
   ```
   
   Alternatively, use the Django development server (limited WebSocket support):
   ```
   python manage.py runserver
   ```

8. Access the application at http://localhost:8000

## Usage

1. **Login**: Access the system using the admin credentials or register a new user
2. **Chat Interface**: Ask questions about projects such as:
   - "Show me all active projects"
   - "Which projects are over budget?"
   - "What's the status of Project X?"
   - "Who are the team members in the Marketing sheet?"
3. **Model Selection**: Toggle between Google Gemini and OpenAI models using the selector at the top
4. **Chat Sessions**: Use the dropdown to create new chat sessions or switch between existing ones
5. **Project Dashboard**: Navigate to the Analytics Dashboard to view usage statistics
6. **Chat History**: Browse past conversations and export important discussions
7. **Starred Messages**: Star important responses for quick reference later

## Advanced Features

### Real-time Chat with WebSockets
The application uses Django Channels and WebSockets to provide real-time chat functionality:
- Instant responses without page reloads
- Typing indicators when the AI is processing
- Connection resilience with automatic fallback to AJAX

### Model Switching
Dynamically switch between AI models:
- Google Gemini 1.5-Flash: Default model with high performance
- OpenAI GPT-4o-mini: Alternative model with different capabilities

### Dashboard Analytics
Track and analyze your chatbot usage:
- Message frequency over time
- Model distribution and usage statistics
- Most active chat sessions

### Chat Session Management
- Create multiple chat sessions for different topics
- Switch between sessions seamlessly
- View, export, and delete past sessions

## Security

The application implements standard Django security practices:
- CSRF protection for all forms
- WebSocket authentication
- XSS protection
- Content-Type sniffing prevention
- X-Frame-Options set to DENY

## Production Deployment

For production deployment, we recommend:
1. Using Daphne or Uvicorn behind a reverse proxy like Nginx
2. Enabling HTTPS for secure WebSocket connections (WSS)
3. Setting up Redis as the channel layer backend
4. Configuring proper database backends (PostgreSQL recommended)

## License

[MIT License](LICENSE)