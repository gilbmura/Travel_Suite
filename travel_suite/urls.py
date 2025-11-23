"""
URL configuration for travel_suite project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api.urls import api_urlpatterns

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Django admin at different path
    path('api/', include(api_urlpatterns)),
    path('', include('api.urls')),  # Frontend routes (includes custom admin routes)
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

