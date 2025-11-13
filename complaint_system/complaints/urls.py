from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('submit-complaint/', views.submit_complaint, name='submit_complaint'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    path('authority/login/', views.authority_login, name='authority_login'),
    path('authority/logout/', views.authority_logout, name='authority_logout'),
    path('authority/', views.authority_landing, name='authority_landing'),
    path('authority/dashboard/', views.authority_dashboard, name='authority_dashboard'),
    path('authority/complaints/<int:pk>/', views.authority_complaint_detail, name='authority_complaint_detail'),
    path('authority/<slug:department_slug>/', views.department_dashboard, name='department_dashboard'),
]
