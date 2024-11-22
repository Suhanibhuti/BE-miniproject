from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect  # Import redirect function

admin.site.site_header = "Advanced Hospital Management Admin"
admin.site.site_title = "Advanced Hospital Management Admin Portal"
admin.site.index_title = "Welcome to Advanced Hospital Management System"

urlpatterns = [
    path('', lambda request: redirect('staff_login')),  # Redirect root to 'staff_login'
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # Include your accounts URLs
]

# Serve static and media files only in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
