from django.urls import path
from . import views

urlpatterns = [
    path('staff_login/', views.staff_login, name='staff_login'),  # Your login path
    path('landing/', views.landing, name='landing'),  # Your login path
    path('logoutp', views.logoutp, name='logoutp'),
    path('logouts', views.logouts, name='logouts'),
    
    
    path('basestaff/', views.basestaff, name='basestaff'),  # Your login path
    
    path('staff_dash/', views.staff_dash, name='staff_dash'),  # Your staff dashboard path
    path('staff_app/', views.staff_app, name='staff_app'),  # Your staff dashboard path
    path('staff_pat/', views.staff_pat, name='staff_pat'),  # Your staff dashboard path
    path('staff_pat1/', views.staff_pat1, name='staff_pat1'),  # Your staff dashboard path
    path('staff_reg/', views.staff_reg, name='staff_reg'),  # Your staff dashboard path
    path('get-schedule/', views.get_schedule, name='get_schedule'),
    path('create-appointment/', views.create_appointment, name='create_appointment'),
    #  path("getAppointments", views.get_appointments, name="get_appointments"),
    
    path('nurse_dash/', views.nurse_dash, name='nurse_dash'),
    path('nurse_pat/', views.nurse_pat, name='nurse_pat'),  # Your staff dashboard path
    path('nurse_pat1/', views.nurse_pat1, name='nurse_pat1'),
    path('nurse_app/', views.nurse_app, name='nurse_app'),
    path('nurse_reg/', views.nurse_reg, name='nurse_reg'),
    
    
    path('admin_dash/', views.admin_dash, name='admin_dash'),
    
    path('login_p/', views.login_p, name='login_p'),  # Your login path
    path('p_dash/', views.p_dash, name='p_dash'),
    path('p_pres/', views.p_pres, name='p_pres'),
    path('p_rep/', views.p_rep, name='p_rep'),
    path('p_det/', views.p_det, name='p_det'),
    path('p_reg/', views.p_reg, name='p_reg'),
    
    
    path('ad_app/', views.ad_app, name='ad_app'), 
     
    path('ad_pat/', views.ad_pat, name='ad_pat'),
    path('edit_patient/<int:patient_id>/', views.edit_patient, name='edit_patient'),
    path('delete_patient/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    path('add_patient/', views.add_patient, name='add_patient'),
    
    
    path('ad_nurse/', views.ad_nurse, name='ad_nurse'),
    path('edit-nurse/<int:nurse_id>/', views.edit_nurse, name='edit_nurse'),
    path('add-nurse/', views.add_nurse, name='add_nurse'),
    path('delete-nurse/<int:nurse_id>/',views.delete_nurse, name='delete_nurse'),
    
    path('ad_doc/', views.ad_doc, name='ad_doc'),
    path('edit_doctor/<int:doctor_id>/', views.edit_doctor, name='edit_doctor'),
    # path('reset_password/<int:user_id>/', views.reset_password, name='reset_password'),
    path('delete_doctor/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),
    path('add_doctor/', views.add_doctor, name='add_doctor'),
    
]
