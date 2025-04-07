from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils.chatbot_service import ChatbotService
from .utils.google_sheets import GoogleSheetsClient

def index(request):
    """
    View for the chatbot interface
    """
    # Get available sheet names to display in the interface
    sheets_client = GoogleSheetsClient()
    sheet_names = sheets_client.get_available_sheet_names()
    
    return render(request, 'chatbot/index.html', {
        'sheet_names': sheet_names
    })

@csrf_exempt
def chat(request):
    """
    API endpoint for chatbot interactions
    """
    if request.method == 'POST':
        try:
            # Parse the request body
            data = json.loads(request.body)
            message = data.get('message', '')
            history = data.get('history', [])
            sheet_name = data.get('sheet_name', None)
            
            # Get response from chatbot service
            chatbot = ChatbotService()
            response = chatbot.get_response(message, sheet_name, history)
            
            return JsonResponse({
                'response': response['response'],
                'source': response['source'],
                'sheet_name': response['sheet_name']
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def projects(request):
    """
    View to display all projects
    """
    chatbot = ChatbotService()
    sheets_client = GoogleSheetsClient()
    sheet_names = sheets_client.get_available_sheet_names()
    
    # Get selected sheet from query parameter, if any
    selected_sheet = request.GET.get('sheet', None)
    if selected_sheet and selected_sheet not in sheet_names:
        selected_sheet = None
        
    project_data = chatbot.get_project_data(selected_sheet)
    
    return render(request, 'chatbot/projects.html', {
        'projects': project_data['projects'],
        'sheet_names': sheet_names,
        'selected_sheet': selected_sheet
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
