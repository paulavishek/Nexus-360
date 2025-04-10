# Project Management Chatbot

## Overview
A Django-based chatbot application that answers questions about projects stored in a database. The chatbot uses OpenAI's GPT-4o-mini as its model.

## Features

- **Project Database**: Access project information from Google Sheets
- **Natural Language Interface**: Ask questions about projects in natural language
- **Dashboard Integration**: View project statistics and analytics
- **Budget Analysis**: Analyze project budgets and identify over/under budget projects
- **Multi-Sheet Support**: Query data across multiple project sheets

## Requirements

- Python 3.9+
- Django 5.0+
- OpenAI API key
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

7. Start the development server:
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
3. **Project Dashboard**: Navigate to the Projects section to see all projects
4. **Budget Analysis**: View budget statistics in the Budget Analysis section

## Advanced Configuration

- **Caching**: Project data is cached for 5 minutes to improve performance
- **Additional Sheets**: Add more Google Sheets by configuring the ADDITIONAL_SHEETS environment variable

## Security

The application implements standard Django security practices:
- CSRF protection for all forms
- XSS protection
- Content-Type sniffing prevention
- X-Frame-Options set to DENY

## License

[MIT License](LICENSE)