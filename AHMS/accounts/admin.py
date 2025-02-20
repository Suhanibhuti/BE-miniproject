from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PatientReg

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
