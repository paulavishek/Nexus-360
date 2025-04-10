from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from .utils.chatbot_service import ChatbotService
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm

@ensure_csrf_cookie
@login_required(login_url='chatbot:login')
def index(request):
    """
    View for the chatbot interface with CSRF protection
    """
    # Create a chatbot service to get available sheet names
    chatbot = ChatbotService()
    sheet_names = chatbot.sheets_client.get_available_sheet_names()
    
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
        refresh_data = data.get('refresh_data', False)  # Option to bypass cache
        
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
        response = chatbot.get_response(message, None, history, use_cache=not refresh_data)
        
        return JsonResponse({
            'response': response['response'],
            'source': response.get('source', 'chat')
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
def refresh_data(request):
    """
    API endpoint to refresh the database cache
    """
    try:
        chatbot = ChatbotService()
        success = chatbot.clear_cache()
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': 'Database cache refreshed successfully. New data is now available.'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to refresh database cache.'
            }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error refreshing database cache: {str(e)}'
        }, status=500)

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
