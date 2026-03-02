from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'transaction_type', 'status', 'created_at')
    list_filter = ('status', 'transaction_type')
    search_fields = ('user__username', 'user__email', 'payment_id')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')

    fieldsets = (
        ('Информация о транзакции', {
            'fields': ('user', 'amount', 'transaction_type', 'status', 'description')
        }),
        ('Данные платежной системы', {
            'fields': ('payment_id', 'payment_method')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )