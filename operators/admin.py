from django.contrib import admin
from .models import OperatorUser, OperatorAssignment


@admin.register(OperatorUser)
class OperatorUserAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'phone_number', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['full_name', 'user__username', 'phone_number', 'email']


@admin.register(OperatorAssignment)
class OperatorAssignmentAdmin(admin.ModelAdmin):
    list_display = ['operator', 'route', 'is_active', 'created_at']
    list_filter = ['is_active', 'route']
    search_fields = ['operator__full_name', 'route__name']

