from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('projects/', views.projects, name='projects'),
    path('projects/<str:project_name>/', views.project_detail, name='project_detail'),
    path('budget-analysis/', views.budget_analysis, name='budget_analysis'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_overview, name='dashboard_overview'),
    path('dashboard/project/<str:project_name>/', views.project_dashboard, name='project_dashboard'),
]