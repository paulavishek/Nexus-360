# Nexus360

<div align="center">
  <p align="center">
  <img src="nexus360_logo.png" alt="Nexus360 Logo" width="300">
</p>
  <h3>Intelligent Project Assistant</h3>
  <p>Your AI-powered companion for project insights</p>
</div>

## 📋 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [User Guide](#-user-guide)
  - [Getting Started](#getting-started)
  - [Using the Chat Interface](#using-the-chat-interface)
  - [Model Selection](#model-selection)
  - [Chat Sessions](#chat-sessions)
  - [Google Search Integration](#google-search-integration)
  - [Dashboard and Analytics](#dashboard-and-analytics)
  - [Sample Questions](#sample-questions)
- [Technical Setup](#-technical-setup)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Google Search API Setup](#google-search-api-setup)
  - [Database Scaling](#database-scaling)
- [Admin Guide](#-admin-guide)
- [Advanced Features](#-advanced-features)
- [Troubleshooting](#-troubleshooting)
- [Security](#-security)
- [Production Deployment](#-production-deployment)

## 🔍 Overview

Nexus360 is an intelligent assistant that connects to your data sources (Google Sheets or SQL databases) and provides natural language answers to your questions. Simply type your questions about projects, budgets, timelines, or team members, and get instant insights powered by OpenAI and Google Gemini AI models. With the new Google Search integration, the chatbot can now also provide up-to-date information from the web to complement its knowledge.

This application brings your project data to life, allowing both technical and non-technical team members to access critical information through a simple conversation interface. No SQL queries or spreadsheet formulas needed!

## ✨ Key Features

- **Flexible Data Source Integration**: 
  - **Google Sheets**: Connect directly to your existing project data in Google Sheets
  - **SQL Databases**: Scale up with MySQL or PostgreSQL for larger datasets
- **Dual AI Models**: Choose between two powerful AI engines:
  - **Google Gemini**: Google's latest AI model for fast, efficient responses
  - **OpenAI**: Access OpenAI's powerful language models for rich, detailed answers
- **Google Search Integration**: Access up-to-date information from the web to overcome AI knowledge cutoffs
- **Natural Language Interface**: Ask questions in plain English about projects, budgets, timelines, resources
- **Real-time Responses**: Get immediate answers through our WebSocket technology
- **Multi-Sheet/Table Support**: Query across multiple data sources (Marketing, Development, etc.)
- **Chat History**: Save all conversations for future reference and knowledge sharing
- **Session Management**: Create multiple chat sessions for different topics or projects
- **Usage Analytics**: Track usage patterns and most frequent questions
- **Model Usage Analytics**: Monitor which AI models are being utilized and their performance
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

### Google Search Integration

The chatbot can now access up-to-date information from the web for questions that require current knowledge:

1. **Automatic Detection**: The system automatically detects when a question might benefit from web search
2. **Seamless Integration**: When the chatbot uses web search data, you'll see source citations in the response
3. **Source Citations**: Responses using web data include links to the original sources [Source: Example Website (URL)]
4. **Toggle Feature**: Administrators can enable/disable this feature through the .env settings

To use the Google Search feature:

1. Simply ask questions that might require up-to-date information, such as:
   - "What are the latest project management trends in 2025?"
   - "How are companies currently handling remote team collaboration?"
   - "What's the current best practice for agile sprint planning?"

2. The chatbot will automatically:
   - Detect that your question needs recent information
   - Search the web for relevant, current data
   - Provide an answer that combines its AI knowledge with web search results
   - Cite sources with links so you can verify the information

### Dashboard and Analytics
 
Access insights about your chatbot usage:

1. Navigate to the Dashboard tab to see usage statistics
2. View charts showing message frequency, model usage, and most active sessions
3. Get insights into which models are being used most frequently

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

#### Web Search Enhanced Questions (using Google Search API)
- "What are the latest project management methodologies in 2025?"
- "How do current economic trends affect project budgeting strategies?"
- "What are the recent changes to agile frameworks that we should consider?"
- "Tell me about the newest project management tools released this year"
- "What best practices have emerged for managing remote project teams?"
- "What were the outcomes of the recent PMI conference?"
- "How are companies currently handling AI integration in project workflows?"

#### SQL Database Queries (when using MySQL/PostgreSQL)
- "Show me the relationship between project budget and timeline delays"
- "Calculate the average completion rate across all teams"
- "Identify which clients have the highest number of change requests"
- "Find patterns in budget overruns across different project types"

## 🛠️ Technical Setup

### Requirements

- Python 3.9+
- Django 5.0+
- Django Channels 4.0+ (for WebSockets)
- OpenAI API key
- Google Gemini API key
- Google Sheets API credentials
- Google Search API credentials
- MySQL or PostgreSQL (for scaled deployments)

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
   
   # Google Search API configuration
   GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
   GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
   ENABLE_WEB_SEARCH=True
   
   # Database configuration (for scaling)
   DB_TYPE=sqlite  # Options: sqlite, mysql, postgresql
   # DB_NAME=your_db_name
   # DB_USER=your_db_username
   # DB_PASSWORD=your_db_password
   # DB_HOST=localhost
   # DB_PORT=5432  # 5432 for PostgreSQL, 3306 for MySQL
   
   # Enable SQL Database for chatbot queries
   USE_SQL_DATABASE=False  # Set to True to use SQL instead of Google Sheets
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

### Google Search API Setup

To enable the Google Search integration, follow these steps:

1. **Create a Google Cloud Project** (or use your existing one):
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select your existing project

2. **Enable the Custom Search API**:
   - In the Google Cloud Console, go to "APIs & Services" > "Library"
   - Search for "Custom Search API" and click on it
   - Click "Enable" to activate the API for your project

3. **Create API Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" and select "API Key"
   - Copy the generated API key

4. **Create a Programmable Search Engine**:
   - Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
   - Click "Add" to create a new search engine
   - Name your search engine (e.g., "PM_ChatBot")
   - Select "Search the entire web" (recommended for general knowledge)
   - Toggle "SafeSearch" ON (recommended)
   - Toggle "Image search" OFF (unless you need image results)
   - Click "Create"
   - After creation, copy your Search Engine ID (a 16-digit code like "16b0e4815604a47f1")

5. **Add Credentials to Environment Variables**:
   - Open your `.env` file
   - Add or update the following variables:
     ```
     GOOGLE_SEARCH_API_KEY=your_copied_api_key_here
     GOOGLE_SEARCH_ENGINE_ID=your_copied_search_engine_id_here
     ENABLE_WEB_SEARCH=True
     ```

6. **Restart Your Application**:
   - Restart your Django server for the changes to take effect

7. **Test the Integration**:
   - Ask a question that requires current information like "What are the latest project management trends in 2025?"
   - The response should include web search results with source citations

**Important Notes**:
- The free tier of Google Custom Search API allows 100 queries per day
- After exceeding the free tier, you will be charged per query (check Google Cloud pricing)
- The system includes retry logic and rate limiting to help manage API usage

### Database Scaling

As your project grows, you can transition from SQLite to more robust database systems:

#### Migrating to PostgreSQL

1. Install PostgreSQL and necessary Python packages:
   ```bash
   pip install psycopg2-binary sqlalchemy
   ```

2. Create a PostgreSQL database:
   ```sql
   CREATE DATABASE pm_chatbot;
   CREATE USER pm_chatbot_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE pm_chatbot TO pm_chatbot_user;
   ```

3. Update your `.env` file:
   ```
   DB_TYPE=postgresql
   DB_NAME=pm_chatbot
   DB_USER=pm_chatbot_user
   DB_PASSWORD=secure_password
   DB_HOST=localhost
   DB_PORT=5432
   USE_SQL_DATABASE=True
   ```

4. Migrate your data:
   ```bash
   python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data_backup.json
   python manage.py migrate
   python manage.py loaddata data_backup.json
   ```

#### Migrating to MySQL

1. Install MySQL and necessary Python packages:
   ```bash
   pip install mysqlclient mysql-connector-python sqlalchemy
   ```

2. Create a MySQL database:
   ```sql
   CREATE DATABASE pm_chatbot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'pm_chatbot_user'@'localhost' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON pm_chatbot.* TO 'pm_chatbot_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. Update your `.env` file:
   ```
   DB_TYPE=mysql
   DB_NAME=pm_chatbot
   DB_USER=pm_chatbot_user
   DB_PASSWORD=secure_password
   DB_HOST=localhost
   DB_PORT=3306
   USE_SQL_DATABASE=True
   ```

4. Migrate your data following the same steps as for PostgreSQL.

#### Using SQL Database for Chatbot Queries

When scaling with a SQL database, you can activate the direct SQL querying feature:

1. Set `USE_SQL_DATABASE=True` in your `.env` file
2. The chatbot will now query your SQL database directly instead of Google Sheets
3. For optimal performance, ensure your database tables are properly indexed
4. Consider setting up read-only credentials for the chatbot to enhance security

#### Benefits of SQL Database Integration

- **Performance**: Handle millions of records with efficient queries
- **Complex Analysis**: Enable multi-table joins and complex aggregations
- **Data Integrity**: Leverage database constraints and relationships
- **Security**: Implement row-level security and user-based permissions
- **Scalability**: Support concurrent users and growing datasets
- **Real-time Updates**: Access the most current data instantly

## 👩‍💼 Admin Guide

As an administrator, you have additional capabilities:

1. **User Management**: Access the Django admin panel (/admin) to manage user accounts
2. **System Monitoring**: View system logs and monitor API usage
3. **Database Management**: Directly access and update the Google Sheets connection
4. **Analytics Access**: View detailed analytics about system usage
5. **Custom Setup**: Configure additional sheets and data connections
6. **Google Search Configuration**: Enable/disable web search and monitor API usage

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

### Google Search Integration
The chatbot can now access recent information from the web:
- **Automatic Detection**: System detects when a question might benefit from web search
- **Source Transparency**: All web-sourced information includes citations with links
- **Knowledge Extension**: Extends the AI models beyond their knowledge cutoff dates
- **Configurable**: Easily enable/disable via environment variables
- **Smart Integration**: Results from web searches are seamlessly blended with AI responses
- **Rate Limiting**: Built-in handling of API rate limits to prevent overages

### Dashboard Analytics
Track and analyze your chatbot usage:
- Message frequency over time
- Model distribution and usage statistics
- Most active chat sessions

### Chat Session Management
- Create multiple chat sessions for different topics
- Switch between sessions seamlessly
- View, export, and delete past sessions

### SQL Database Integration
- Direct natural language queries to SQL databases
- Automatic SQL query generation from plain English questions
- Support for complex joins and aggregations
- Built-in safeguards against harmful queries
- Explanation of query results in plain language
- Support for visualization of query results

## ❓ Troubleshooting

**Q: The chatbot doesn't understand my question**  
A: Try rephrasing your question to be more specific. Include project names, dates, or specific terms that match your Google Sheets data.

**Q: I'm seeing an error about API limits**  
A: This happens when you've reached the usage limits for the AI models or Google Search API. Wait a few minutes before trying again or switch to the other model.

**Q: The data seems outdated**  
A: Click the refresh icon before asking your question to get the latest data from Google Sheets.

**Q: The web search isn't providing current information**  
A: Make sure your Google Search API is correctly configured in the .env file and that you haven't exceeded the daily quota (100 queries for free tier).

**Q: The chatbot mentions sources but doesn't include the full source information**  
A: Restart the application after configuring the Google Search API. This ensures the improved source citation format is applied.

**Q: How do I disable the web search feature?**  
A: Set `ENABLE_WEB_SEARCH=False` in your .env file and restart the application.

**Q: The chatbot is slow to respond**  
A: Complex questions analyzing large datasets or requiring web searches may take longer. Try splitting your question into smaller parts.

**Q: I lost my chat history**  
A: Chat sessions are saved per user. Make sure you're logged in with the correct account and check the session dropdown.

**Q: How do I switch from Google Sheets to SQL database?**  
A: Update your `.env` file with the appropriate database credentials and set `USE_SQL_DATABASE=True`. Also, ensure your data is properly migrated to the database.

**Q: The chatbot doesn't understand my database schema**  
A: For complex database schemas, try providing more context in your questions by mentioning table names or key columns. You can also improve performance by ensuring proper indexing on frequently queried columns.

## 🔒 Security

The application implements standard Django security practices:
- CSRF protection for all forms
- WebSocket authentication
- XSS protection
- Content-Type sniffing prevention
- X-Frame-Options set to DENY
- Google Sheets API used with limited-scope credentials
- Google Search API with content filtering enabled
- SQL query sanitization to prevent injection attacks
- Optional read-only database user for chatbot queries

## 🚀 Production Deployment

For production deployment, we recommend:
1. Using Daphne or Uvicorn behind a reverse proxy like Nginx
2. Enabling HTTPS for secure WebSocket connections (WSS)
3. Setting up Redis as the channel layer backend
4. **Configuring Production Database**:
   - PostgreSQL or MySQL with connection pooling
   - Regular database backups and point-in-time recovery
   - Database replication for high availability
   - Proper indexing for optimized query performance
5. Implementing monitoring for API usage and system performance
6. Setting up a content delivery network (CDN) for static assets


---

<div align="center">
  <p>Developed by Avishek Paul</p>
  <p>© 2025 All Rights Reserved</p>
</div>
