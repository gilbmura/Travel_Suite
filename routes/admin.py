from django.contrib import admin
from .models import District, Route


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'origin', 'destination', 'distance_km', 'is_active', 'created_at']
    list_filter = ['is_active', 'origin', 'destination']
    search_fields = ['name', 'origin__name', 'destination__name']

