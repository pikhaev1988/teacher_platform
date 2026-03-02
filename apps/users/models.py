from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    """Расширенная модель пользователя"""
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=15, blank=True, verbose_name='Телефон')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')

    # Поля для подписки
    subscription_active = models.BooleanField(default=False, verbose_name='Подписка активна')
    subscription_end_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания подписки')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Баланс')

    # Статистика
    total_generations = models.PositiveIntegerField(default=0, verbose_name='Всего генераций')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def activate_subscription(self, days=30):
        """Активировать подписку на указанное количество дней"""
        self.subscription_active = True
        if self.subscription_end_date and self.subscription_end_date > timezone.now():
            self.subscription_end_date += timedelta(days=days)
        else:
            self.subscription_end_date = timezone.now() + timedelta(days=days)
        self.save()

    def can_generate(self):
        """Проверка возможности генерации"""
        if self.subscription_active and self.subscription_end_date > timezone.now():
            return True
        return self.balance >= 10  # Минимальная стоимость генерации

    def debit_generation(self):
        """Списание средств за генерацию"""
        if self.subscription_active and self.subscription_end_date > timezone.now():
            # Если есть подписка, не списываем с баланса
            return True
        elif self.balance >= 10:
            self.balance -= 10
            self.save()
            return True
        return False