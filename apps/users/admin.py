from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'subscription_active', 'balance')
    list_filter = ('subscription_active', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Информация о подписке', {
            'fields': ('subscription_active', 'subscription_end_date', 'balance', 'total_generations', 'phone', 'avatar')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('email', 'first_name', 'last_name', 'phone')
        }),
    )