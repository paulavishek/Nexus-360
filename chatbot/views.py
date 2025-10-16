from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from .utils.chatbot_service import ChatbotService
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, F, Q
from django.utils import timezone
import datetime
from .forms import UserRegistrationForm
from .models import ChatSession, ChatMessage, ChatAnalytics, UserPreference

@ensure_csrf_cookie
@login_required(login_url='chatbot:login')
def index(request):
    """
    View for the chatbot interface with CSRF protection
    """
    # Create a chatbot service to get available sheet names
    chatbot = ChatbotService()
    sheet_names = chatbot.sheets_client.get_available_sheet_names()
    
    # Get user preferences
    user_preferences, created = UserPreference.objects.get_or_create(user=request.user)
    
    # Get active chat session or create a new one
    active_session = ChatSession.objects.filter(user=request.user, is_active=True).first()
    if not active_session:
        active_session = ChatSession.objects.create(user=request.user)
    
    # Get previous chat sessions
    previous_sessions = ChatSession.objects.filter(
        user=request.user, 
        is_active=False
    ).order_by('-updated_at')[:10]  # Get last 10 sessions
    
    return render(request, 'chatbot/index.html', {
        'sheet_names': sheet_names,
        'active_session_id': active_session.id,
        'previous_sessions': previous_sessions,
        'user_preferences': user_preferences,
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
        selected_model = data.get('model', 'gemini')  # Get selected model (gemini/openai)
        session_id = data.get('session_id')
        sheet_name = data.get('sheet_name', '')
        
        # Validate inputs
        if not message or len(message.strip()) == 0:
            return JsonResponse({
                'error': 'Message cannot be empty'
            }, status=400)
            
        # Limit history size
        if history and len(history) > 50:  # Reasonable limit
            history = history[-50:]  # Keep only the last 50 messages
        
        # Get or create session
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                # If session doesn't exist or doesn't belong to user, create a new one
                session = ChatSession.objects.create(user=request.user)
        else:
            # Get active session or create new one
            session = ChatSession.objects.filter(user=request.user, is_active=True).first()
            if not session:
                session = ChatSession.objects.create(user=request.user)
        
        # Save user message to database
        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=message
        )
        
        # Update session's last activity time
        session.save()  # This updates the updated_at field
        
        # Get response from chatbot service
        chatbot = ChatbotService()
        
        # Override default model if needed
        if selected_model == 'openai':
            # Swap OpenAI to be primary
            temp = chatbot.gemini_client
            chatbot.gemini_client = chatbot.openai_client
            chatbot.openai_client = temp
        
        # Prepare context with sheet name if provided
        context = None
        if sheet_name:
            context = f"Focus on data from the '{sheet_name}' sheet for this query."
            
        response = chatbot.get_response(message, context, history, use_cache=not refresh_data)
        
        # Save assistant response to database
        ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=response['response'],
            model=response.get('source', 'gemini')
        )
        
        # Update analytics with proper error handling
        try:
            today = timezone.now().date()
            analytics, created = ChatAnalytics.objects.get_or_create(
                user=request.user, 
                date=today,
                defaults={
                    'messages_sent': 0,
                    'gemini_requests': 0,
                    'openai_requests': 0
                }
            )
            analytics.messages_sent += 1
            
            # Increment the appropriate counter based on which model was used
            if response.get('source') == 'gemini':
                analytics.gemini_requests += 1
            elif response.get('source') in ['openai', 'openai-fallback']:
                analytics.openai_requests += 1
                
            analytics.save()
        except Exception as analytics_error:
            # Log the error but don't fail the request
            print(f"Error updating analytics: {analytics_error}")
        
        return JsonResponse({
            'response': response['response'],
            'source': response.get('source', 'chat'),
            'session_id': session.id
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

def welcome_view(request):
    """
    Landing page that directs users to either login or register
    If already authenticated, redirects to the chatbot interface
    """
    if request.user.is_authenticated:
        return redirect('chatbot:index')
    
    return render(request, 'chatbot/welcome.html')

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
def dashboard(request):
    """
    Analytics dashboard view
    """
    # Get date range for filtering
    end_date = timezone.now().date()
    start_date = end_date - datetime.timedelta(days=30)  # Last 30 days
    
    # Get overall usage statistics
    total_messages = ChatMessage.objects.filter(
        session__user=request.user,
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    ).count()
    
    # Get model usage breakdown
    model_usage = ChatMessage.objects.filter(
        session__user=request.user,
        role='assistant',
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    ).values('model').annotate(count=Count('id'))
    
    # Format model usage for chart
    model_labels = []
    model_data = []
    model_colors = []
    for item in model_usage:
        model_labels.append(item['model'] or 'Unknown')
        model_data.append(item['count'])
        if item['model'] == 'gemini':
            model_colors.append('#4285F4')  # Google blue
        elif item['model'] == 'openai':
            model_colors.append('#10A37F')  # OpenAI green
        elif item['model'] == 'openai-fallback':
            model_colors.append('#F4B400')  # Yellow
        else:
            model_colors.append('#9E9E9E')  # Grey
    
    # Get daily activity
    daily_activity = ChatMessage.objects.filter(
        session__user=request.user,
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    ).values('timestamp__date').annotate(count=Count('id')).order_by('timestamp__date')
    
    # Format daily activity for chart
    date_labels = []
    date_data = []
    for item in daily_activity:
        date_labels.append(item['timestamp__date'].strftime('%Y-%m-%d'))
        date_data.append(item['count'])
    
    # Get most active chat sessions
    active_sessions = ChatSession.objects.filter(
        user=request.user,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).annotate(message_count=Count('messages')).order_by('-message_count')[:5]
    
    return render(request, 'chatbot/dashboard.html', {
        'total_messages': total_messages,
        'model_labels': json.dumps(model_labels),
        'model_data': json.dumps(model_data),
        'model_colors': json.dumps(model_colors),
        'date_labels': json.dumps(date_labels),
        'date_data': json.dumps(date_data),
        'active_sessions': active_sessions,
    })

@login_required(login_url='chatbot:login') 
def chat_history(request):
    """
    View for browsing user's chat history
    """
    sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')
    
    # Handle session deletion
    if request.method == "POST" and 'delete_session' in request.POST:
        session_id = request.POST.get('delete_session')
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            session.delete()
            messages.success(request, "Chat session deleted successfully.")
            return redirect('chatbot:chat_history')
        except ChatSession.DoesNotExist:
            messages.error(request, "Chat session not found.")
    
    # Handle session export
    if request.method == "GET" and 'export_session' in request.GET:
        session_id = request.GET.get('export_session')
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            # Logic for exporting (will be implemented separately)
            messages.success(request, "Export feature will be implemented soon.")
        except ChatSession.DoesNotExist:
            messages.error(request, "Chat session not found.")
    
    return render(request, 'chatbot/chat_history.html', {
        'sessions': sessions
    })

@login_required(login_url='chatbot:login')
def view_chat_session(request, session_id):
    """
    View for displaying a specific chat session
    """
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
        messages = session.messages.all().order_by('timestamp')
        
        return render(request, 'chatbot/view_session.html', {
            'session': session,
            'chat_messages': messages
        })
    except ChatSession.DoesNotExist:
        messages.error(request, "Chat session not found or you don't have permission to view it.")
        return redirect('chatbot:chat_history')

@login_required(login_url='chatbot:login')
@require_POST
def save_preferences(request):
    """
    API endpoint to save user preferences
    """
    try:
        data = json.loads(request.body)
        
        # Get or create user preferences
        prefs, created = UserPreference.objects.get_or_create(user=request.user)
        
        # Update fields if they exist in the request
        if 'theme' in data and data['theme'] in ['light', 'dark']:
            prefs.theme = data['theme']
        
        if 'default_model' in data and data['default_model'] in ['gemini', 'openai']:
            prefs.default_model = data['default_model']
        
        prefs.save()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required(login_url='chatbot:login')
@require_POST
def create_new_session(request):
    """
    Create a new chat session and set it as active
    """
    try:
        # Deactivate all current active sessions
        ChatSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
        
        # Create new session
        session = ChatSession.objects.create(user=request.user, is_active=True)
        
        return JsonResponse({
            'status': 'success',
            'session_id': session.id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required(login_url='chatbot:login')
@require_POST
def switch_session(request):
    """
    Switch to an existing chat session
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        # Validate session exists and belongs to user
        session = ChatSession.objects.get(id=session_id, user=request.user)
        
        # Deactivate all current active sessions
        ChatSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
        
        # Set the selected session as active
        session.is_active = True
        session.save()
        
        # Get the messages for this session
        messages = [{
            'role': msg.role,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'model': msg.model
        } for msg in session.messages.all().order_by('timestamp')]
        
        return JsonResponse({
            'status': 'success',
            'session_id': session.id,
            'messages': messages
        })
    except ChatSession.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Session not found or you do not have permission to access it.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required(login_url='chatbot:login')
def get_session_messages(request, session_id):
    """
    API endpoint to get all messages for a specific chat session
    """
    try:
        # Verify session belongs to the requesting user
        session = ChatSession.objects.get(id=session_id, user=request.user)
        
        # Get all messages for the session
        messages_queryset = session.messages.all().order_by('timestamp')
        
        # Format messages for response
        messages = [{
            'id': msg.id,
            'role': msg.role,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'model': msg.model
        } for msg in messages_queryset]
        
        return JsonResponse({
            'status': 'success',
            'session_id': session_id,
            'messages': messages
        })
    except ChatSession.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Session not found or you do not have permission to access it.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required(login_url='chatbot:login')
@require_POST
def reset_chat_history(request):
    """
    API endpoint to reset chat history for the current active session
    """
    try:
        # Get the active session for the current user
        active_session = ChatSession.objects.filter(user=request.user, is_active=True).first()
        
        if active_session:
            # Delete all messages in this session
            ChatMessage.objects.filter(session=active_session).delete()
            
            # Update the session title if needed
            active_session.title = None
            active_session.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Chat history has been reset successfully.'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'No active chat session found.'
            }, status=404)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required(login_url='chatbot:login')
def refresh_model_data(request):
    """
    API endpoint to get fresh model distribution data without reloading the page
    """
    try:
        # Get date range for filtering
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=30)  # Last 30 days
        
        # Get model usage breakdown
        model_usage = ChatMessage.objects.filter(
            session__user=request.user,
            role='assistant',
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        ).values('model').annotate(count=Count('id'))
        
        # Format model usage for chart
        model_labels = []
        model_data = []
        model_colors = []
        for item in model_usage:
            model_labels.append(item['model'] or 'Unknown')
            model_data.append(item['count'])
            if item['model'] == 'gemini':
                model_colors.append('#4285F4')  # Google blue
            elif item['model'] == 'openai':
                model_colors.append('#10A37F')  # OpenAI green
            elif item['model'] == 'openai-fallback':
                model_colors.append('#F4B400')  # Yellow
            else:
                model_colors.append('#9E9E9E')  # Grey
        
        # Get total messages count for stats
        total_messages = ChatMessage.objects.filter(
            session__user=request.user,
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        ).count()
        
        # Calculate percentages for the progress bar
        gemini_value = 0
        openai_value = 0
        
        for i, label in enumerate(model_labels):
            if 'gemini' in label:
                gemini_value = model_data[i]
            elif 'openai' in label:
                openai_value = model_data[i]
        
        total_value = gemini_value + openai_value
        gemini_percent = 0
        openai_percent = 0
        
        if total_value > 0:
            gemini_percent = round((gemini_value / total_value) * 100)
            openai_percent = round((openai_value / total_value) * 100)
        
        return JsonResponse({
            'status': 'success',
            'model_labels': model_labels,
            'model_data': model_data,
            'model_colors': model_colors,
            'total_messages': total_messages,
            'gemini_value': gemini_value,
            'openai_value': openai_value,
            'gemini_percent': gemini_percent,
            'openai_percent': openai_percent,
            'has_data': total_value > 0
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
