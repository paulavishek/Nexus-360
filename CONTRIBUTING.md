# Contributing to Nexus360

Thank you for your interest in contributing to Nexus360! This document provides guidelines and instructions for contributing to this project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Setting Up Development Environment](#setting-up-development-environment)
  - [Understanding the Codebase](#understanding-the-codebase)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Guidelines](#development-guidelines)
  - [Coding Standards](#coding-standards)
  - [Testing](#testing)
  - [Documentation](#documentation)
- [Branch Organization](#branch-organization)
- [Review Process](#review-process)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it are governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to avishek-paul@outlook.com.

## Getting Started

### Setting Up Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```
   git clone https://github.com/avishekpaul1310/pm_chatbot.git
   cd pm_chatbot
   ```
3. **Set up upstream remote**:
   ```
   git remote add upstream https://github.com/ORIGINAL_OWNER/pm_chatbot.git
   ```
4. **Create and activate a virtual environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
5. **Install development dependencies**:
   ```
   pip install -r requirements.txt
   ```
6. **Set up configuration**:
   - Copy `.env.example` to `.env` (create if necessary)
   - Populate with your API keys and configuration options
   - For development purposes, you may want to use sandbox/test API keys

### Understanding the Codebase

The project follows a standard Django structure with some custom components:

- `chatbot/` - The main application directory
  - `utils/` - Contains AI clients (OpenAI and Gemini) and service components
  - `consumers.py` - WebSocket handling for real-time chat
  - `models.py` - Data models for chat sessions, messages, etc.
  - `views.py` - View functions for the application
- `project_chatbot/` - The Django project settings directory
- `templates/` - HTML templates for the frontend
- `staticfiles/` - CSS, JS, and other static assets

## How to Contribute

### Reporting Bugs

When reporting bugs, please include:

1. **Description** of the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs actual behavior
4. **Environment details** (Python version, Django version, browser, OS)
5. **Screenshots** if applicable
6. **Relevant logs** from the console or application logs

Use the issue tracker on GitHub to report bugs.

### Suggesting Enhancements

Feature requests and suggestions are welcome. Please provide:

1. **Clear description** of the proposed feature
2. **Use case** explaining why this feature would be beneficial
3. **Possible implementation** approach if you have ideas

### Pull Requests

1. **Create a branch** from the `main` branch with a descriptive name:
   ```
   git checkout -b feature/your-feature-name
   ```
   or
   ```
   git checkout -b fix/issue-you-are-fixing
   ```

2. **Make your changes** following the coding standards

3. **Write or update tests** as needed

4. **Update documentation** to reflect your changes

5. **Commit your changes** with clear commit messages:
   ```
   git commit -m "feat: add ability to filter projects by status"
   ```
   or
   ```
   git commit -m "fix: resolve issue with model selection not persisting"
   ```

6. **Push to your fork**:
   ```
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request** against the `main` branch of the original repository

## Development Guidelines

### Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) coding style for Python code
- Use 4 spaces for indentation
- Keep line length to a maximum of 100 characters
- Include docstrings for all functions, classes, and methods
- Use meaningful variable and function names
- Follow Django's [coding style](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)

### Testing

- Write tests for new features and bug fixes
- Run the existing test suite before submitting:
  ```
  python manage.py test
  ```
- Aim for high test coverage for critical components, especially:
  - AI model integration
  - Google Sheets data handling
  - WebSocket communication

### Documentation

- Update the README.md if introducing new features or changing setup instructions
- Document complex functions and classes with clear docstrings
- For frontend changes, update any relevant user documentation

## Branch Organization

- `main` - The production branch; stable releases only
- `develop` - Integration branch for features
- `feature/*` - Feature branches
- `fix/*` - Bug fix branches
- `release/*` - Release preparation branches
- `hotfix/*` - Emergency fixes for production

## Review Process

1. Automated checks will run on your pull request
2. Maintainers will review your code for:
   - Functionality
   - Code quality
   - Test coverage
   - Documentation
3. Changes may be requested before merging
4. Once approved, a maintainer will merge your pull request

## Working with AI Models

When contributing to the AI model integrations:

1. **Test both models**: Ensure your changes work with both OpenAI and Gemini
2. **Handle API limits**: Implement appropriate rate limiting and error handling
3. **Minimize token usage**: Optimize prompts to reduce API costs
4. **Respect fallback order**: Maintain the model fallback mechanisms

## Community

- Join our [community forum/chat] to discuss development
- Check the [project roadmap] for planned features
- Participate in [community calls] to discuss project direction

---

Thank you for contributing to Nexus360! Your efforts help make this tool better for everyone.