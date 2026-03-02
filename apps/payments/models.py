from django.db import models
from django.conf import settings


class Transaction(models.Model):
    """Транзакция платежа"""
    TRANSACTION_TYPES = [
        ('subscription', 'Оплата подписки'),
        ('topup', 'Пополнение баланса'),
        ('generation', 'Списание за генерацию'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('success', 'Успешно'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возврат'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions',
                             verbose_name='Пользователь')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name='Тип транзакции')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')

    # Данные от платежной системы
    payment_id = models.CharField(max_length=255, blank=True, verbose_name='ID платежа')
    payment_method = models.CharField(max_length=100, blank=True, verbose_name='Метод оплаты')
    description = models.TextField(blank=True, verbose_name='Описание')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.amount} руб. ({self.get_status_display()})'