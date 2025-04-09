from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json
from .utils.chatbot_service import ChatbotService
from .utils.google_sheets import GoogleSheetsClient
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm
from .utils.dashboard_service import DashboardService

@ensure_csrf_cookie
@login_required(login_url='chatbot:login')
def index(request):
    """
    View for the chatbot interface with CSRF protection
    """
    # Get available sheet names to display in the interface
    sheets_client = GoogleSheetsClient()
    sheet_names = sheets_client.get_available_sheet_names()
    
    return render(request, 'chatbot/index.html', {
        'sheet_names': sheet_names
    })

@login_required(login_url='chatbot:login')
@require_POST
def chat(request):
    """
    API endpoint for chatbot interactions with CSRF protection
    """
    try:
        # Parse the request body
        data = json.loads(request.body)
        message = data.get('message', '')
        history = data.get('history', [])
        sheet_name = data.get('sheet_name', None)
        
        # Validate inputs
        if not message or len(message.strip()) == 0:
            return JsonResponse({
                'error': 'Message cannot be empty'
            }, status=400)
            
        # Limit history size
        if history and len(history) > 50:  # Reasonable limit
            history = history[-50:]  # Keep only the last 50 messages
        
        # Get response from chatbot service
        chatbot = ChatbotService()
        response = chatbot.get_response(message, sheet_name, history)
        
        # Check if it's a dashboard response
        if response.get('source') == 'dashboard':
            return JsonResponse({
                'response': response['response'],
                'source': response['source'],
                'sheet_name': response['sheet_name'],
                'dashboard_url': response['dashboard_url']
            })
        
        return JsonResponse({
            'response': response['response'],
            'source': response['source'],
            'sheet_name': response['sheet_name']
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required(login_url='chatbot:login')
def projects(request):
    """
    View to display all projects with pagination
    """
    chatbot = ChatbotService()
    sheets_client = GoogleSheetsClient()
    sheet_names = sheets_client.get_available_sheet_names()
    
    # Get selected sheet from query parameter, if any
    selected_sheet = request.GET.get('sheet', None)
    if selected_sheet and selected_sheet not in sheet_names:
        selected_sheet = None
        
    # Get search query if any
    search_query = request.GET.get('search', None)
    
    # Get project data
    project_data = chatbot.get_project_data(selected_sheet)
    projects_list = project_data['projects']
    
    # Rename the _source_sheet attribute to source_sheet (without underscore)
    for project in projects_list:
        if '_source_sheet' in project:
            project['source_sheet'] = project['_source_sheet']
            # Optionally remove the original attribute to save memory
            # del project['_source_sheet']
    
    # Filter projects if search query is provided
    if search_query:
        search_query = search_query.lower()
        filtered_projects = []
        for project in projects_list:
            # Search in name, description and status
            if (search_query in project.get('name', '').lower() or 
                search_query in project.get('description', '').lower() or 
                search_query in project.get('status', '').lower()):
                filtered_projects.append(project)
        projects_list = filtered_projects
    
    # Sort projects by name (or could use another field)
    projects_list = sorted(projects_list, key=lambda x: x.get('name', '').lower())
    
    # Pagination
    page = request.GET.get('page', 1)
    items_per_page = 9  # 3x3 grid layout
    paginator = Paginator(projects_list, items_per_page)
    
    try:
        projects_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        projects_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        projects_page = paginator.page(paginator.num_pages)
    
    return render(request, 'chatbot/projects.html', {
        'projects': projects_page,
        'sheet_names': sheet_names,
        'selected_sheet': selected_sheet,
        'search_query': search_query,
        'total_projects': len(projects_list)
    })

@login_required(login_url='chatbot:login')
def project_detail(request, project_name):
    """
    View to display details of a specific project
    """
    # Get sheet name from query parameter, if any
    sheet_name = request.GET.get('sheet', None)
    
    chatbot = ChatbotService()
    sheets_client = chatbot.sheets_client
    
    # Get project details
    project = sheets_client.get_project_by_name(project_name, sheet_name)
    if not project:
        return render(request, 'chatbot/project_not_found.html')
    
    # Rename the _source_sheet attribute to source_sheet (without underscore)
    if '_source_sheet' in project:
        project['source_sheet'] = project['_source_sheet']
    
    # Get the sheet name from the project if it exists
    project_sheet = project.get('source_sheet', sheet_name)
    
    # Get project members
    members = sheets_client.get_project_members(project_name=project_name, sheet_name=project_sheet)
    
    # Rename _source_sheet for members too if needed
    for member in members:
        if '_source_sheet' in member:
            member['source_sheet'] = member['_source_sheet']
    
    return render(request, 'chatbot/project_detail.html', {
        'project': project,
        'members': members,
        'sheet_name': project_sheet
    })

@login_required(login_url='chatbot:login')
def budget_analysis(request):
    """
    View to display budget analysis
    """
    chatbot = ChatbotService()
    sheets_client = chatbot.sheets_client
    sheet_names = sheets_client.get_available_sheet_names()
    
    # Get selected sheet from query parameter, if any
    selected_sheet = request.GET.get('sheet', None)
    if selected_sheet and selected_sheet not in sheet_names:
        selected_sheet = None
    
    budget_stats = sheets_client.get_budget_statistics(selected_sheet)
    
    return render(request, 'chatbot/budget_analysis.html', {
        'budget_stats': budget_stats,
        'sheet_names': sheet_names,
        'selected_sheet': selected_sheet
    })

def login_view(request):
    """
    View for user login
    """
    # If user is already logged in, redirect to chat interface
    if request.user.is_authenticated:
        return redirect('chatbot:index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to the page the user was trying to access
            next_url = request.GET.get('next', 'chatbot:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
            
    return render(request, 'chatbot/login.html')

def logout_view(request):
    """
    View for user logout
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('chatbot:login')

def register_view(request):
    """View for user registration"""
    if request.user.is_authenticated:
        return redirect('chatbot:index')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. You can now log in.')
            return redirect('chatbot:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'chatbot/register.html', {'form': form})

@login_required(login_url='chatbot:login')
def dashboard_overview(request):
    """
    View for overall dashboard
    """
    dashboard_service = DashboardService()
    
    # Get selected sheet from query parameter, if any
    sheet_name = request.GET.get('sheet', None)
    
    # Get dashboard data
    dashboard_data = dashboard_service.generate_project_dashboard(sheet_name=sheet_name)
    
    # Get available sheet names
    sheets_client = dashboard_service.sheets_client
    sheet_names = sheets_client.get_available_sheet_names()
    
    return render(request, 'chatbot/dashboard_overview.html', {
        'dashboard': dashboard_data,
        'sheet_names': sheet_names,
        'selected_sheet': sheet_name
    })

@login_required(login_url='chatbot:login')
def project_dashboard(request, project_name):
    """
    View for project-specific dashboard
    """
    try:
        dashboard_service = DashboardService()
        
        # Get sheet name from query parameter, if any
        sheet_name = request.GET.get('sheet', None)
        
        # Get dashboard data
        dashboard_data = dashboard_service.generate_project_dashboard(
            project_name=project_name, 
            sheet_name=sheet_name
        )
        
        if 'error' in dashboard_data:
            messages.error(request, dashboard_data['error'])
            return render(request, 'chatbot/project_not_found.html')
        
        return render(request, 'chatbot/project_dashboard.html', {
            'dashboard': dashboard_data,
            'project_name': project_name,
            'sheet_name': sheet_name
        })
    except Exception as e:
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in project_dashboard view: {e}")
        
        # Show error message to user
        messages.error(request, f"An error occurred while loading the project dashboard: {str(e)}")
        
        # Redirect to project not found page
        return render(request, 'chatbot/project_not_found.html')
