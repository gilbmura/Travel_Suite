"""
URL Configuration for Travel Suite API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationViewSet, UserViewSet, CustomerViewSet, RouteViewSet,
    VehicleViewSet, SeatViewSet, EventViewSet, BookingViewSet, 
    TicketViewSet, PaymentViewSet, TransactionViewSet
)

# Create a router and register ViewSets
router = DefaultRouter()
router.register(r'auth', UserRegistrationViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='user')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'seats', SeatViewSet, basename='seat')
router.register(r'events', EventViewSet, basename='event')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
]
