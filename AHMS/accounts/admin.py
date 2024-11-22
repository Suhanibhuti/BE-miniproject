from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    
    # Display only username, password, and role in the user list
    list_display = ['username', 'role']

    # Limit the fields shown when creating/editing a user to username, password, and role
    fieldsets = (
        (None, {'fields': ('username', 'password', 'role')}),
    )

    # This is to ensure the password field appears correctly in the admin interface
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role')}
        ),
    )
    
admin.site.register(User, CustomUserAdmin)
