from django.urls import path
from . import views

urlpatterns = [
    path('staff_login/', views.staff_login, name='staff_login'),  # Your login path
    path('landing/', views.landing, name='landing'),  # Your login path
    path('logoutp', views.logoutp, name='logoutp'),
    path('logouts', views.logouts, name='logouts'),
    
    
    path('basestaff/', views.basestaff, name='basestaff'),  # Your login path
    
    path('staff_dash/', views.staff_dash, name='staff_dash'), 
    path('staff_app/', views.staff_app, name='staff_app'), 
    path('staff_pat/', views.staff_pat, name='staff_pat'),  
    path('staff_pat1/<int:patient_id>/', views.staff_pat1, name='staff_pat1'),
    
    path('staff_pat_pres/<int:patient_id>/', views.staff_pat_pres, name='staff_pat_pres'),
    path('add_prescription/<int:patient_id>/', views.add_prescription, name='add_prescription'), 
    
    path('staff_pat_rep/<int:patient_id>/', views.staff_pat_rep, name='staff_pat_rep'),
    path('add_comment/<int:patient_id>/', views.add_comment, name='add_comment'),
    
    path('staff_pat_dialysis/<int:patient_id>/', views.staff_pat_dialysis, name='staff_pat_dialysis'),
    path('staff_pat_eyecare/<int:patient_id>/', views.staff_pat_eyecare, name='staff_pat_eyecare'),
    path('staff_pat_cardio/<int:patient_id>/', views.staff_pat_cardio, name='staff_pat_cardio'),
    
    
    
    path('staff_reg/', views.staff_reg, name='staff_reg'),  # Your staff dashboard path
    path('get-schedule/', views.get_schedule, name='get_schedule'),
    path('create-appointment/', views.create_appointment, name='create_appointment'),
    #  path("getAppointments", views.get_appointments, name="get_appointments"),
    
    path('nurse_dash/', views.nurse_dash, name='nurse_dash'),
    
    path('nurse_pat/', views.nurse_pat, name='nurse_pat'),  # Your staff dashboard path
    path('nurse_pat1/<int:patient_id>/', views.nurse_pat1, name='nurse_pat1'),
    path('nurse_pat_pres/<int:patient_id>/', views.nurse_pat_pres, name='nurse_pat_pres'),
    path('nurse_pat_rep/<int:patient_id>/', views.nurse_pat_rep, name='nurse_pat_rep'),
    
    path('nurse_pat_dialysis/<int:patient_id>/', views.nurse_pat_dialysis, name='nurse_pat_dialysis'),
    path('add_tubing/', views.add_tubing, name='add_tubing'),
    path('delete_tubing/', views.delete_tubing, name='delete_tubing'),
    
    
    path('nurse_pat_eyecare/<int:patient_id>/', views.nurse_pat_eyecare, name='nurse_pat_eyecare'),
    path('nurse_pat_cardio/<int:patient_id>/', views.nurse_pat_cardio, name='nurse_pat_cardio'),
    
    
    path('nurse_app/', views.nurse_app, name='nurse_app'),
    path('nurse_reg/', views.nurse_reg, name='nurse_reg'),
    
    
    path('admin_dash/', views.admin_dash, name='admin_dash'),
    path('get_department_data/', views.get_department_data, name='get_department_data'),
    path('get_patient_metrics/', views.get_patient_metrics, name='get_patient_metrics'),
    
    path('login_p/', views.login_p, name='login_p'),  # Your login path
    
    path('p_dash/', views.p_dash, name='p_dash'),
    path('get_doctors_by_department/', views.get_doctors_by_department, name='get_doctors_by_department'),
    path('get_doctor_details/', views.get_doctor_details, name='get_doctors_by_department'),
    
    
    path('p_pres/', views.p_pres, name='p_pres'),
    path('send-reminders/<str:date>/', views.send_reminders, name='send_reminders'),
    path('prescription_list/', views.prescription_list, name='prescription_list'),
    path('prescriptions/toggle_reminders/<int:prescription_id>/', views.toggle_reminders, name='toggle_reminders'),
    
    
    path('p_rep/', views.p_rep, name='p_rep'),
    path('delete_report/<int:report_id>/', views.delete_report, name='delete_report'),
    
    path('p_det/', views.p_det, name='p_det'),
    path('p_reg/', views.p_reg, name='p_reg'),
    path('p_dialysis/', views.p_dialysis, name='p_dialysis'),
    path('fetch_tubing_data/', views.fetch_tubing_data, name='fetch_tubing_data'),
    
    path('fetch_weight_data/', views.fetch_weight_data, name='fetch_weight_data'),
    path('add_weight/', views.add_weight, name='add_weight'),
    path('delete_weight/', views.delete_weight, name='delete_weight'),
    
    path('patient/<int:patient_id>/fetch_weight_data/', views.fetch_weight_data, name='fetch_weight_data'),
    path('patient/<int:patient_id>/add_weight/', views.add_weight, name='add_weight'),
    path('patient/<int:patient_id>/delete_weight/', views.delete_weight, name='delete_weight'),
    
    path('fetch_water_intake/', views.fetch_water_intake, name='fetch_water_intake'),
    path('fetch_water_history/', views.fetch_water_history, name='fetch_water_history'),
    
    path('add_water_intake/', views.add_water_intake, name='add_water_intake'),
    path('delete-water-intake/', views.delete_water_intake, name='delete_water_intake'),
    
    path('p_cardio/', views.p_cardio, name='p_cardio'),
    path('p_cholesterol/', views.p_cholesterol, name='p_cholesterol'),
    path('p_ecg/', views.p_ecg, name='p_ecg'),
    
    path('p_eyecare/', views.p_eyecare, name='p_eyecare'),
    
    
    path('ad_app/', views.ad_app, name='ad_app'), 
    path('ad_rep/', views.ad_rep, name='ad_rep'), 
     
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
    
    path('accept-appointment/<int:appointment_id>/', views.accept_appointment, name='accept_appointment'),
    path('reject-appointment/<int:appointment_id>/', views.reject_appointment, name='reject_appointment'),
    # path('send_email/', views.send_email, name='send_email'),
    
]
