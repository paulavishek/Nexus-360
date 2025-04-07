from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json
from .utils.chatbot_service import ChatbotService
from .utils.google_sheets import GoogleSheetsClient
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST

@ensure_csrf_cookie
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
    
    # Get the sheet name from the project if it exists
    project_sheet = project.get('_source_sheet', sheet_name)
    
    # Get project members
    members = sheets_client.get_project_members(project_name=project_name, sheet_name=project_sheet)
    
    return render(request, 'chatbot/project_detail.html', {
        'project': project,
        'members': members,
        'sheet_name': project_sheet
    })

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
