from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PatientReg, StaffD, WorkingHour, Appointment,NurseReg,PatientReport,Prescription,WaterIntake,WeightTracking,DialysisTubing,DoctorComment,EyeExam

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'role']  # Display username and role
    fieldsets = (
        (None, {'fields': ('username', 'password', 'role')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role')}
        ),
    )

admin.site.register(User, CustomUserAdmin)

class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'mobile_number', 'age', 'gender', 'blood_group')

admin.site.register(PatientReg, PatientAdmin)


class WorkingHourInline(admin.TabularInline):
    model = WorkingHour
    extra = 1  # Allows adding one working hour inline by default
    
@admin.register(StaffD)
class StaffD(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'department', 'years_of_experience')

@admin.register(WorkingHour)
class WorkingHourAdmin(admin.ModelAdmin):
    list_display = ('staff', 'start_time', 'end_time')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'start_time','end_time','date')



class NurseAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'mobile_number', 'department')

admin.site.register(NurseReg, NurseAdmin)
admin.site.register(PatientReport)
admin.site.register(Prescription)
admin.site.register(DoctorComment)

admin.site.register(WeightTracking)
admin.site.register(WaterIntake)
admin.site.register(DialysisTubing)
admin.site.register(EyeExam)
