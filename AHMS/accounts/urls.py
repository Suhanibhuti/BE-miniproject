from django.urls import path
from . import views

urlpatterns = [
    path('staff_login/', views.staff_login, name='staff_login'),  # Your login path
    path('landing/', views.landing, name='landing'),  # Your login path
    path('staff_dash/', views.staff_dash, name='staff_dash'),  # Your staff dashboard path
    path('staff_app/', views.staff_app, name='staff_app'),  # Your staff dashboard path
    path('staff_pat/', views.staff_pat, name='staff_pat'),  # Your staff dashboard path
    path('staff_pat1/', views.staff_pat1, name='staff_pat1'),  # Your staff dashboard path
    # Add other URLs here as needed
    
    path('nurse_dash/', views.nurse_dash, name='nurse_dash'),
    path('nurse_pat/', views.nurse_pat, name='nurse_pat'),  # Your staff dashboard path
    path('nurse_pat1/', views.nurse_pat1, name='nurse_pat1'),
    path('nurse_app/', views.nurse_app, name='nurse_app'),
    
    path('admin_dash/', views.admin_dash, name='admin_dash'),
]
