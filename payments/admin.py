from django.contrib import admin
from .models import PaymentTransaction, Refund


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'provider', 'amount', 'status', 'booking', 'created_at']
    list_filter = ['provider', 'status', 'created_at']
    search_fields = ['provider_transaction_id', 'idempotency_key', 'booking__passenger_name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment_transaction', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['provider_refund_id']
    readonly_fields = ['id', 'created_at', 'updated_at']

