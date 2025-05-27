# Nexus360

<p align="center">
  <img src="nexus360_logo.png" alt="Nexus360 Logo" width="300">
</p>
<h3 align="center">Intelligent Project Assistant</h3>
<p align="center">Your AI-powered companion for project insights</p>

## 📋 Table of Contents

- [What is Nexus360?](#what-is-nexus360)
- [Cool Things Nexus360 Can Do](#cool-things-nexus360-can-do)
- [How to Use Nexus360 (For Everyone!)](#how-to-use-nexus360-for-everyone)
  - [Getting Started](#getting-started)
  - [Chatting with Nexus360](#chatting-with-nexus360)
  - [Choosing Your AI Brain (Model Selection)](#choosing-your-ai-brain-model-selection)
  - [Keeping Chats Organized (Chat Sessions)](#keeping-chats-organized-chat-sessions)
  - [Super-Smart Answers with Google Search (RAG)](#super-smart-answers-with-google-search-rag)
  - [What is RAG? (Retrieval Augmented Generation)](#what-is-rag-retrieval-augmented-generation)
  - [Seeing How You Use Nexus360 (Dashboard and Analytics)](#seeing-how-you-use-nexus360-dashboard-and-analytics)
  - [Example Questions to Ask](#example-questions-to-ask)
- [For the Tech-Savvy (Technical Setup)](#for-the-tech-savvy-technical-setup)
  - [What You Need](#what-you-need)
  - [Getting it Running](#getting-it-running)
  - [Setting Things Up (Configuration)](#setting-things-up-configuration)
  - [Connecting to Google Search](#connecting-to-google-search)
  - [Using Bigger Databases](#using-bigger-databases)
- [For System Admins (Admin Guide)](#for-system-admins-admin-guide)
- [Extra Cool Tech Features](#extra-cool-tech-features)
- [Help! Something Went Wrong (Troubleshooting)](#help-something-went-wrong-troubleshooting)
- [Keeping Things Safe (Security)](#keeping-things-safe-security)
- [Using Nexus360 for Real (Production Deployment)](#using-nexus360-for-real-production-deployment)

## 🤔 What is Nexus360?

Nexus360 is like a super-smart helper for your projects. Imagine you have a lot of project information stored in spreadsheets (like Google Sheets) or databases. Instead of digging through all that data yourself, you can just ask Nexus360 questions in plain English!

For example, you can ask:

- "Which projects are running late?"
- "How much money is left for the 'New Website' project?"
- "Who is working on the marketing campaign?"

Nexus360 uses powerful AI "brains" (from Google Gemini and OpenAI) to understand your questions and find the answers in your data. Plus, it can even use Google Search to find the very latest information on the web if your question is about something new or very current. This makes it a **Retrieval Augmented Generation (RAG)** system – a fancy way of saying it finds information and then uses it to give you a great answer.

It’s designed so that anyone on your team, whether you love tech stuff or not, can easily get the project information they need, just by chatting.

## ✨ Cool Things Nexus360 Can Do

- **Connects to Your Data**: Works with Google Sheets or bigger SQL databases (like MySQL or PostgreSQL).
- **Two AI Brains**: You can pick between Google Gemini (super fast) or OpenAI (great for complex questions).
- **Google Search Power**: Gets the latest info from the web for up-to-the-minute answers (this is the RAG part!).
- **Talk Normally**: Ask questions in everyday language.
- **Quick Answers**: Get information fast, like you're texting.
- **Handles Lots of Data**: Can look through many different spreadsheets or database tables at once.
- **Saves Your Chats**: Keeps a history of your conversations so you can look back.
- **Organized Chats**: Start new chats for different topics or projects.
- **See How It's Used**: Check out graphs and stats on how Nexus360 is helping.
- **Works Anywhere**: Use it on your computer, tablet, or phone.
- **Smart Backup**: If one AI brain has a problem, it can switch to the other one automatically.

## 📱 How to Use Nexus360 (For Everyone!)

### Getting Started

1.  **Go to the App**: Open the Nexus360 website link your admin gives you.
2.  **Log In**: Type in your username and password.
3.  **New Here?**: If it's your first time, you might need to click "Register" to make an account.

### Chatting with Nexus360

It’s just like using a messaging app:

1.  **Ask Away**: Type your question in the box at the bottom of the screen and hit Enter or click Send.
2.  **See the Answer**: Nexus360 will reply in the chat window.
3.  **Save Important Info**: Click the star icon next to an answer if you want to easily find it later.
4.  **Fresh Data**: If your data changes often (like in Google Sheets), click the "Refresh Data" button before asking to make sure Nexus360 has the latest info.
5.  **Follow-Up Questions**: Nexus360 remembers what you’ve talked about in the current chat, so you can ask more questions based on previous answers.

### Choosing Your AI Brain (Model Selection)

You can tell Nexus360 which AI brain to use:

1.  Look for the model selector (it might be a toggle or dropdown) at the top of the chat.
2.  Choose "OpenAI" or "Gemini." Try both to see which one you like best for different types of questions!
3.  Nexus360 will remember your choice for next time.

### Keeping Chats Organized (Chat Sessions)

Keep your conversations neat and tidy:

1.  **New Chat**: Click "New Chat" (or similar) to start a brand-new conversation on a new topic.
2.  **Switch Chats**: Look for a list or dropdown of your past chats to open an old one.
3.  **Rename Chats**: Usually, there's a little pencil icon to change a chat's name to something more memorable.
4.  **Delete Chats**: A trash can icon will let you remove chats you don't need anymore.

### Super-Smart Answers with Google Search (RAG)

Sometimes, your questions might be about very recent topics or things your project data doesn't cover. That's where Google Search comes in!

1.  **It's Automatic**: Nexus360 is smart enough to know when your question might need fresh info from the web.
2.  **Clear and Honest**: If Nexus360 uses Google Search, it will tell you where it got the information by showing you the source (like "[Source: Example Website (URL)]").
3.  **Always Learning**: This helps the AI give you answers even about things that happened after it was last trained.

**How to use it:**

Just ask your question! If it’s something like:

- "What are the newest project management tools for 2025?"
- "How are other companies using AI in project management right now?"

Nexus360 will figure out it needs to search the web, find relevant info, and then give you an answer that combines its AI smarts with what it found online.

### What is RAG? (Retrieval Augmented Generation)

You might hear the term **RAG** when we talk about Nexus360's Google Search feature. It stands for **Retrieval Augmented Generation**.

Here's what it means in simple terms:

1.  **Retrieval (Find Stuff)**: When you ask a question, especially one needing current info, Nexus360 first *retrieves* (finds and pulls out) relevant information. This could be from your project data or, in this case, from Google Search results.
2.  **Augmented (Make it Better)**: The information it finds is then used to *augment* (add to or improve) what the AI already knows. It gives the AI extra, up-to-date context.
3.  **Generation (Create the Answer)**: Finally, the AI *generates* (creates) an answer for you, using both its built-in knowledge AND the new information it just found.

So, RAG is just a fancy way of saying Nexus360 doesn't just rely on what it was taught; it actively looks for new information to give you the best, most current answers possible! This makes it much smarter and more helpful, especially for topics that change quickly.

### Seeing How You Use Nexus360 (Dashboard and Analytics)

Curious about how much you or your team are using Nexus360?

1.  Look for a "Dashboard" or "Analytics" tab or link.
2.  Here you can see charts and stats, like how many messages are sent, which AI brain is used most, and which chat topics are popular.

### Example Questions to Ask

Here are some ideas to get you started:

**About Your Projects:**

- "Show me all projects that are currently active."
- "What's the status of the 'Website Update' project?"
- "Which projects are supposed to finish this month?"

**About Money and Budgets:**

- "Are any projects over budget?"
- "How much money is left for the 'Marketing Push' project?"
- "Show me the top 5 projects by budget."

**About Deadlines and Schedules:**

- "When is the 'Mobile App Launch' planned?"
- "Which projects have deadlines in the next two weeks?"

**About Your Team:**

- "Who is working on the 'Client Demo' project?"
- "Show me all developers on the team."

**Questions Using Web Search (RAG examples for current info):**

- "What are the latest trends in project management for 2025?"
- "How are companies using AI in project management today?"
- "What new project tools came out this year?"

## For the Tech-Savvy (Technical Setup)

This part is for those who will be installing and managing Nexus360.

### What You Need

- Python (version 3.9 or newer)
- Django (a web framework, version 5.0 or newer)
- Django Channels (for live chat, version 4.0 or newer)
- API keys (special codes to connect to services) for:
  - OpenAI
  - Google Gemini
  - Google Sheets
  - Google Search
- A database like MySQL or PostgreSQL if you have a LOT of data (otherwise, SQLite works fine for smaller setups).

### Getting it Running

1.  **Download the Code**: Usually from a place like GitHub.

    ```bash
    git clone https://github.com/yourusername/pm_chatbot.git
    cd pm_chatbot
    ```

2.  **Set Up a Virtual Space**: This keeps all the project's code bits separate.

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the Parts**: This command reads a list of all the bits Nexus360 needs and installs them.

    ```bash
    pip install -r requirements.txt
    ```

### Setting Things Up (Configuration)

1.  **Create a Secret File (`.env`)**: In the main project folder, make a file named `.env`. This is where you'll put all your secret keys and settings. Here's an example of what goes in it:

    ```env
    # Django settings
    DJANGO_SECRET_KEY=your_very_secret_django_key_here # Make this long and random!
    DEBUG=True  # Set to False for real-world use
    ALLOWED_HOSTS=localhost,127.0.0.1 # Add your server address for real-world use

    # API keys
    OPENAI_API_KEY=your_openai_api_key_here
    GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here

    # Google Sheets (where your project data might be)
    GOOGLE_SHEETS_CREDENTIALS_FILE=path/to/your/google_sheets_credentials.json # A special file from Google
    GOOGLE_SHEETS_PROJECT_DB=the_id_of_your_main_google_sheet
    
    # Optional: If you have more Google Sheets to connect
    # ADDITIONAL_SHEETS=SheetName1:sheet_id_1,SheetName2:sheet_id_2
    
    # Google Search API (for RAG)
    GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
    GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_from_google_here
    ENABLE_WEB_SEARCH=True # Set to False to turn off Google Search
    
    # Database (SQLite is default, good for starting)
    DB_TYPE=sqlite
    # If using MySQL or PostgreSQL, you'll add more lines here for name, user, password, etc.
    # DB_NAME=your_db_name
    # DB_USER=your_db_username
    # DB_PASSWORD=your_db_password
    # DB_HOST=localhost
    # DB_PORT=5432  # 5432 for PostgreSQL, 3306 for MySQL
    
    # Tell Nexus360 to use your big database for answers (instead of Google Sheets)
    USE_SQL_DATABASE=False  # Set to True if you set up MySQL/PostgreSQL above
    ```

2.  **Prepare the Database**:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

3.  **Create an Admin User**: This user can manage Nexus360 from a special admin page.

    ```bash
    python manage.py create_admin --username youradmin --password yourstrongpassword --email admin@example.com
    ```

4.  **Start the App**: For the best experience with live chat, use Daphne.

    ```bash
    daphne project_chatbot.asgi:application -p 8000
    ```

    Or, for simpler testing (live chat might not be as smooth):

    ```bash
    python manage.py runserver
    ```

5.  **Open in Browser**: Go to `http://localhost:8000` in your web browser.

### Connecting to Google Search

To let Nexus360 use Google Search (for the RAG feature):

1.  **Google Cloud Project**: You need a project in Google Cloud Console. Create one if you don't have it.
2.  **Turn on "Custom Search API"**: In your Google Cloud project, find this API in the "Library" and enable it.
3.  **Get an API Key**: In "Credentials," create a new API Key. Copy this key.
4.  **Create a Programmable Search Engine**:
    - Go to the [Programmable Search Engine](https://programmablesearchengine.google.com/) site.
    - Click "Add" to make a new search engine.
    - Give it a name (e.g., "Nexus360_Search").
    - Choose "Search the entire web."
    - Turn "SafeSearch" ON.
    - Turn "Image search" OFF (unless you need it).
    - Click "Create."
    - After it's made, find and copy its "Search Engine ID" (it's a long code).

5.  **Put Keys in `.env` File**: Add/update these lines in your `.env` file:

    ```env
    GOOGLE_SEARCH_API_KEY=paste_your_api_key_here
    GOOGLE_SEARCH_ENGINE_ID=paste_your_search_engine_id_here
    ENABLE_WEB_SEARCH=True
    ```

6.  **Restart Nexus360**: Stop and start the app so it sees the new settings.

7.  **Test It**: Ask a question that needs very current info, like "What are the latest AI trends in 2025?" You should see answers that mention web sources.

**Important Notes on Google Search**:

- Google gives you 100 free searches per day. After that, they charge a small amount per search.
- Nexus360 tries to be smart about not using the API too much.

### Using Bigger Databases

If you have tons of data, SQLite might get slow. You can switch to PostgreSQL or MySQL.

**Switching to PostgreSQL (Example)**:

1.  **Install PostgreSQL tools**: `pip install psycopg2-binary sqlalchemy`
2.  **Set up a PostgreSQL database**: Create a database and a user for Nexus360.
3.  **Update `.env` file**: Change `DB_TYPE` to `postgresql` and add your database details (name, user, password, host, port). Set `USE_SQL_DATABASE=True`.
4.  **Move Your Data**: This is a bit technical. You'll need to back up data from SQLite and load it into PostgreSQL, then run `python manage.py migrate`.

(Similar steps apply for MySQL, just with different tools and settings.)

**Why use a bigger database?**

- **Faster**: Handles millions of records better.
- **More Powerful Questions**: Can do more complex data analysis.
- **Safer Data**: Better tools for keeping data secure and backed up.

## 👩‍💼 For System Admins (Admin Guide)

If you're managing Nexus360 for your team:

1.  **Manage Users**: Go to the `/admin` page on your Nexus360 website to add users, change passwords, etc.
2.  **Keep an Eye on Things**: Check system logs and how much the APIs (OpenAI, Gemini, Google Search) are being used.
3.  **Data Connections**: Manage how Nexus360 connects to Google Sheets or your SQL database.
4.  **Check Usage Stats**: Look at the analytics dashboard to see how the team is using the app.
5.  **Google Search Settings**: You can turn the web search feature on or off in the `.env` file.

## 🔧 Extra Cool Tech Features

- **Live Chat**: Uses WebSockets so answers appear instantly without reloading the page.
- **Switch AI Brains**: Easily change between Google Gemini and OpenAI.
- **Smart Web Search (RAG)**:
  - Figures out when to search the web.
  - Clearly shows where web info came from.
  - Helps the AI know about brand new topics.
  - Can be turned on/off.
- **Usage Dashboard**: See charts on how the chatbot is being used.
- **Organized Chat History**: Manage multiple conversations easily.
- **Talk to SQL Databases**: If you connect a SQL database, you can ask complex questions about your data in plain English, and Nexus360 tries to figure out the technical SQL query for you!

## ❓ Help! Something Went Wrong (Troubleshooting)

### Q: Nexus360 doesn't understand my question

**A:** Try asking in a different way. Be more specific. Use names or dates that are in your project data.

### Q: It says "API limit reached"

**A:** This means you've used the AI (OpenAI/Gemini) or Google Search too much for a short period (often there are daily or monthly free limits). Wait a bit and try again, or try switching to the other AI model.

### Q: The project data seems old

**A:** If you're using Google Sheets, click the "Refresh Data" button in the chat interface before asking your question.

### Q: Web search isn't giving me new info

**A:** Double-check that the Google Search API Key and Engine ID are correct in your `.env` file. Also, make sure you haven't used up your 100 free daily searches.

### Q: It mentions web sources but doesn't show the links properly

**A:** Make sure you restart Nexus360 after setting up the Google Search API in the `.env` file.

### Q: How do I turn off the Google Search feature

**A:** In the `.env` file, change `ENABLE_WEB_SEARCH=True` to `ENABLE_WEB_SEARCH=False` and restart Nexus360.

### Q: Nexus360 is slow

**A:** Very complex questions or questions that need a lot of web searching can take a bit longer. Try breaking your question into smaller parts.

### Q: I can't find my old chats

**A:** Make sure you are logged in with the correct account. Your chats are saved under your username. Check the list of your chat sessions.

### Q: How do I switch from using Google Sheets to a big SQL database

**A:** This is a technical step. You need to set up your SQL database (like PostgreSQL or MySQL), update the `.env` file with its details, set `USE_SQL_DATABASE=True`, and then carefully move your data from Google Sheets into the new database.

## 🔒 Keeping Things Safe (Security)

Nexus360 uses standard security measures for web apps:

- Protects against common web attacks.
- Keeps your chat sessions private.
- Uses Google API connections carefully with limited permissions.
- Tries to prevent harmful database queries if connected to SQL.

## 🚀 Using Nexus360 for Real (Production Deployment)

This is for tech teams making Nexus360 available for many users:

1.  Use robust web servers like Daphne or Uvicorn, often with Nginx.
2.  Use HTTPS (secure web connections) for everything, especially live chat.
3.  For busy sites, use Redis to help manage live chat messages.
4.  **Database**: Use a strong database like PostgreSQL or MySQL. Set up regular backups.

---

*Nexus360 - Making project data easy to understand for everyone.*
