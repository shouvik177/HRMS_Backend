from django.urls import path
from . import views, auth_views

urlpatterns = [
    path('employees/', views.employee_list_create),
    path('employees/<int:pk>/', views.employee_detail),
    path('attendance/', views.attendance_list_create),
    path('auth/register/', auth_views.register),
    path('auth/login/', auth_views.login),
    path('auth/logout/', auth_views.logout),
]
