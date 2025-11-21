from django.contrib import admin
from .models import Bus


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'capacity', 'company_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'company_name']
    search_fields = ['plate_number', 'company_name']

