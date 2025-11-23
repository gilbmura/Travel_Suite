"""
API URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import admin_views

router = DefaultRouter()
router.register(r'districts', views.DistrictViewSet, basename='district')
router.register(r'routes', views.RouteViewSet, basename='route')
router.register(r'schedules', views.ScheduleOccurrenceViewSet, basename='schedule')
router.register(r'bookings', views.BookingViewSet, basename='booking')
router.register(r'operator/bookings', views.OperatorBookingViewSet, basename='operator-booking')

# API routes (included under /api/)
api_urlpatterns = [
    path('', include(router.urls)),
    path('operator/schedules/<int:schedule_id>/mark_departed/', views.mark_schedule_departed, name='mark-departed'),
    # Admin management endpoints
    path('admin/districts/', admin_views.admin_districts, name='admin-districts'),
    path('admin/districts/<int:pk>/', admin_views.admin_district_detail, name='admin-district-detail'),
    path('admin/routes/', admin_views.admin_routes, name='admin-routes'),
    path('admin/routes/<int:pk>/', admin_views.admin_route_detail, name='admin-route-detail'),
    path('admin/buses/', admin_views.admin_buses, name='admin-buses'),
    path('admin/buses/<int:pk>/', admin_views.admin_bus_detail, name='admin-bus-detail'),
    path('admin/schedule-recurrences/', admin_views.admin_schedule_recurrences, name='admin-schedule-recurrences'),
    path('admin/schedule-recurrences/<int:pk>/', admin_views.admin_schedule_recurrence_detail, name='admin-schedule-recurrence-detail'),
    path('admin/bookings/', admin_views.admin_bookings, name='admin-bookings'),
    path('admin/operators/', admin_views.admin_operators, name='admin-operators'),
    path('admin/operators/<int:pk>/', admin_views.admin_operator_detail, name='admin-operator-detail'),
    path('admin/operator-assignments/', admin_views.admin_operator_assignments, name='admin-operator-assignments'),
    path('admin/operator-assignments/<int:pk>/', admin_views.admin_operator_assignment_detail, name='admin-operator-assignment-detail'),
]

# Frontend routes (included at root)
urlpatterns = [
    path('', views.index_view, name='index'),
    path('routes/', views.routes_view, name='routes'),
    path('schedules/', views.schedules_view, name='schedules'),
    path('booking/', views.booking_view, name='booking'),
    path('operator/login/', views.operator_login_view, name='operator-login'),
    path('operator/logout/', views.operator_logout_view, name='operator-logout'),
    path('operator/dashboard/', views.operator_dashboard_view, name='operator-dashboard'),
    # Custom admin routes
    path('admin/', views.admin_login_view, name='admin-login'),
    path('admin/logout/', views.admin_logout_view, name='admin-logout'),
    path('admin/dashboard/', views.admin_dashboard_view, name='admin-dashboard'),
]

