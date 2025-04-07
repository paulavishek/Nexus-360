# Project Management Chatbot

A Django-based chatbot application that answers questions about projects stored in a database. The chatbot uses OpenAI's GPT-4o-mini as the primary model with Google Gemini as a fallback.

## Features

- **Project-specific AI Chatbot**: Answer questions about projects, team members, budgets, and more
- **Google Sheets Integration**: Use Google Sheets as an initial database (with future migration path to MySQL/PostgreSQL)
- **Fallback Strategy**: Automatically switches to Google Gemini if OpenAI API fails
- **Project Dashboard**: View all projects, their statuses, and budget information
- **Budget Analysis**: See which projects are over/under budget with visual indicators
- **Responsive Design**: Works on desktop and mobile devices

## Setup Instructions

### Prerequisites

- Python 3.7+
- Django 4.0+
- Google Sheets API credentials
- OpenAI API key
- Google Gemini API key

### Installation

1. Clone the repository or download the source code

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Update the `.env` file with your API keys:
   ```
   # OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Google Gemini API key
   GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key_here
   
   # Google Sheets credentials
   GOOGLE_SHEETS_CREDENTIALS_FILE=path_to_your_google_credentials.json
   GOOGLE_SHEETS_PROJECT_DB=your_google_sheets_id_here
   ```

5. Set up your Google Sheets:
   - Create a new Google Sheet with two worksheets: "Projects" and "Members"
   - The "Projects" worksheet should have columns: name, description, start_date, end_date, budget, expenses, status
   - The "Members" worksheet should have columns: project_name, name, role, email
   
6. Run database migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

8. Access the application at http://localhost:8000

## Google Sheets Setup

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Google Sheets API and Google Drive API
3. Create a service account and download the JSON credentials file
4. Share your Google Sheet with the service account email address (with editor permission)
5. Update the `.env` file with the path to the credentials file and your Google Sheet ID

## Usage

- **Chatbot**: Ask questions about projects, team sizes, budget information, etc.
- **Projects View**: Browse all projects and see their status at a glance
- **Budget Analysis**: Get insights into which projects are over or under budget

## Future Enhancements

- Migration from Google Sheets to MySQL or PostgreSQL
- User authentication and role-based access
- Admin interface for managing projects and team members
- Email notifications for budget alerts
- Custom chatbot training with project-specific documentation

## License

MIT License