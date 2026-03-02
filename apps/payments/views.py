from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import json
from .services import YooKassaService
from .models import Transaction


@login_required
def tariffs(request):
    """Страница с тарифами"""
    context = {
        'subscription_price': 200,
        'topup_options': [100, 300, 500, 1000],
    }
    return render(request, 'payments/tariffs.html', context)


@login_required
@require_POST
def create_payment(request):
    """Создание платежа"""
    payment_type = request.POST.get('payment_type')
    amount = request.POST.get('amount')

    if not payment_type or not amount:
        messages.error(request, 'Не указан тип платежа или сумма')
        return redirect('payments:tariffs')

    try:
        amount = float(amount)
        if amount < 10:
            messages.error(request, 'Минимальная сумма платежа 10 рублей')
            return redirect('payments:tariffs')
    except ValueError:
        messages.error(request, 'Некорректная сумма')
        return redirect('payments:tariffs')

    service = YooKassaService()

    if payment_type == 'subscription':
        description = 'Оплата подписки на 30 дней'
    elif payment_type == 'topup':
        description = f'Пополнение баланса на {amount} руб.'
    else:
        messages.error(request, 'Некорректный тип платежа')
        return redirect('payments:tariffs')

    result = service.create_payment(
        user=request.user,
        amount=amount,
        payment_type=payment_type,
        description=description
    )

    # Сохраняем ID транзакции в сессии для отслеживания
    request.session['last_transaction_id'] = result['transaction'].id

    return redirect(result['payment_url'])


@login_required
def payment_success(request):
    """Страница успешной оплаты"""
    transaction_id = request.session.get('last_transaction_id')

    if transaction_id:
        try:
            transaction = Transaction.objects.get(id=transaction_id, user=request.user)
            if transaction.status == 'success':
                messages.success(request, 'Оплата прошла успешно!')
            else:
                # Проверяем статус платежа через API
                # (для простоты оставим как есть)
                messages.info(request, 'Платеж обрабатывается. Проверьте статус в истории транзакций.')
        except Transaction.DoesNotExist:
            pass

        # Очищаем сессию
        del request.session['last_transaction_id']

    return redirect('users:dashboard')


@login_required
def payment_failed(request):
    """Страница ошибки оплаты"""
    messages.error(request, 'Оплата не прошла. Попробуйте снова или выберите другой способ оплаты.')
    return redirect('payments:tariffs')


@csrf_exempt
@require_POST
def yookassa_webhook(request):
    """
    Webhook для уведомлений от YooKassa
    """
    service = YooKassaService()
    result = service.handle_webhook(request.body.decode('utf-8'))

    if result['success']:
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'error': result.get('error', 'Unknown error')}, status=400)


@login_required
def transaction_history(request):
    """История транзакций"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'transactions': transactions,
    }
    return render(request, 'payments/history.html', context)