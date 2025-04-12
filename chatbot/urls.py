from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('refresh-data/', views.refresh_data, name='refresh_data'),
    
    # New URL patterns for enhanced features
    path('dashboard/', views.dashboard, name='dashboard'),
    path('chat-history/', views.chat_history, name='chat_history'),
    path('session/<int:session_id>/', views.view_chat_session, name='view_session'),
    path('session/<int:session_id>/messages/', views.get_session_messages, name='get_session_messages'),
    path('save-preferences/', views.save_preferences, name='save_preferences'),
    path('create-session/', views.create_new_session, name='create_session'),
    path('switch-session/', views.switch_session, name='switch_session'),
    path('reset-chat/', views.reset_chat_history, name='reset_chat'),
    path('refresh-model-data/', views.refresh_model_data, name='refresh_model_data'),
]