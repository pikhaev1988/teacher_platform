import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from yookassa import Configuration, Payment
from yookassa.domain.notification import WebhookNotification
from .models import Transaction


class YooKassaService:
    """Сервис для работы с YooKassa"""

    def __init__(self):
        Configuration.account_id = settings.YOOKASSA_SHOP_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    def create_payment(self, user, amount, payment_type, description):
        """
        Создание платежа в YooKassa
        """
        # Создаем транзакцию в БД
        transaction = Transaction.objects.create(
            user=user,
            amount=amount,
            transaction_type=payment_type,
            description=description
        )

        idempotence_key = str(uuid.uuid4())

        payment = Payment.create({
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"{settings.SITE_URL}/payments/success/"
            },
            "capture": True,
            "description": description,
            "metadata": {
                "transaction_id": transaction.id,
                "user_id": user.id
            }
        }, idempotence_key)

        # Обновляем транзакцию
        transaction.payment_id = payment.id
        transaction.save()

        return {
            'transaction': transaction,
            'payment_url': payment.confirmation.confirmation_url
        }

    def handle_webhook(self, request_body):
        """
        Обработка webhook уведомления от YooKassa
        """
        try:
            notification = WebhookNotification(request_body)
            payment = notification.object

            if notification.event == 'payment.succeeded':
                # Получаем транзакцию из метаданных
                transaction_id = payment.metadata.get('transaction_id')
                transaction = Transaction.objects.get(id=transaction_id)

                # Обновляем статус транзакции
                transaction.status = 'success'
                transaction.completed_at = timezone.now()
                transaction.payment_method = payment.payment_method.type if hasattr(payment, 'payment_method') else ''
                transaction.save()

                # Начисляем средства пользователю
                self._credit_user_balance(transaction)

                return {'success': True, 'message': 'Payment succeeded'}

            elif notification.event == 'payment.canceled':
                transaction_id = payment.metadata.get('transaction_id')
                transaction = Transaction.objects.get(id=transaction_id)
                transaction.status = 'failed'
                transaction.completed_at = timezone.now()
                transaction.save()

                return {'success': False, 'message': 'Payment canceled'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _credit_user_balance(self, transaction):
        """Начисление средств пользователю"""
        user = transaction.user

        if transaction.transaction_type == 'subscription':
            # Активируем подписку на 30 дней
            user.activate_subscription(30)
        elif transaction.transaction_type == 'topup':
            # Пополняем баланс
            user.balance += transaction.amount
            user.save()