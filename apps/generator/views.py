#apps/generator/views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils import timezone
from django.core.files.base import ContentFile
from .models import GenerationRequest, GeneratedDocument, Subject, Grade
from .forms import GenerationRequestForm
from .services import GPTService, DocumentGenerator


@login_required
def create_request(request):
    """Создание нового запроса на генерацию (синхронно, без Celery)"""

    # Проверяем возможность генерации
    if not request.user.can_generate():
        messages.warning(
            request,
            'У вас недостаточно средств. Пополните баланс или оформите подписку.'
        )
        return redirect('payments:tariffs')

    if request.method == 'POST':
        form = GenerationRequestForm(request.POST)
        if form.is_valid():
            generation_request = form.save(commit=False)
            generation_request.user = request.user
            generation_request.status = 'processing'
            generation_request.save()

            if not request.user.debit_generation():
                messages.warning(
                    request,
                    'У вас недостаточно средств. Пополните баланс или оформите подписку.'
                )
                generation_request.status = 'failed'
                generation_request.error_message = 'Недостаточно средств для генерации'
                generation_request.completed_at = timezone.now()
                generation_request.save()
                return redirect('payments:tariffs')

            try:
                gpt_service = GPTService()
            except Exception as e:
                generation_request.status = 'failed'
                generation_request.error_message = str(e)
                generation_request.completed_at = timezone.now()
                generation_request.save()
                messages.error(
                    request,
                    'Ошибка подключения к GigaChat. Попробуйте позже или обратитесь в поддержку.'
                )
                return redirect('generator:create')

            doc_generator = DocumentGenerator()

            result = gpt_service.generate_lesson_plan(
                topic=generation_request.topic,
                grade=generation_request.grade,
                subject=generation_request.subject,
            )

            if not result.get('success'):
                generation_request.status = 'failed'
                generation_request.error_message = result.get('error', 'Ошибка генерации')
                generation_request.completed_at = timezone.now()
                generation_request.save()
                messages.error(
                    request,
                    f"Ошибка генерации: {generation_request.error_message}"
                )
                return redirect('generator:create')

            generation_request.prompt_tokens = result.get('prompt_tokens', 0)
            generation_request.completion_tokens = result.get('completion_tokens', 0)

            try:
                docx_stream = doc_generator.create_docx_from_markdown(
                    result['text'],
                    generation_request.topic,
                )
                pptx_stream = doc_generator.create_pptx_from_markdown(
                    result['text'],
                    generation_request.topic,
                )

                documents = GeneratedDocument.objects.create(
                    request=generation_request,
                    docx_text=result['text'],
                )

                docx_filename = f"lesson_plan_{generation_request.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.docx"
                documents.docx_file.save(
                    docx_filename,
                    ContentFile(docx_stream.getvalue()),
                )

                pptx_filename = f"presentation_{generation_request.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pptx"
                documents.pptx_file.save(
                    pptx_filename,
                    ContentFile(pptx_stream.getvalue()),
                )

                generation_request.status = 'completed'
                generation_request.completed_at = timezone.now()
                generation_request.save()

                user = generation_request.user
                user.total_generations += 1
                user.save()

                messages.success(request, 'Материалы успешно сгенерированы!')
                return redirect('generator:request_status', request_id=generation_request.id)

            except Exception as e:
                generation_request.status = 'failed'
                generation_request.error_message = str(e)
                generation_request.completed_at = timezone.now()
                generation_request.save()
                messages.error(
                    request,
                    'Произошла ошибка при сохранении файлов. Попробуйте позже.'
                )
                return redirect('generator:create')
    else:
        form = GenerationRequestForm()

    # Получаем список классов для формы
    grades = Grade.objects.all()

    context = {
        'form': form,
        'grades': grades,
        'subjects': Subject.objects.all(),
    }
    return render(request, 'generator/create.html', context)


@login_required
def request_status(request, request_id):
    """Страница статуса генерации"""
    generation_request = get_object_or_404(
        GenerationRequest,
        id=request_id,
        user=request.user
    )

    context = {
        'request': generation_request,
    }
    return render(request, 'generator/status.html', context)


@login_required
def get_status_json(request, request_id):
    """API для получения статуса генерации (для AJAX)"""
    generation_request = get_object_or_404(
        GenerationRequest,
        id=request_id,
        user=request.user
    )

    data = {
        'status': generation_request.status,
        'status_display': generation_request.get_status_display(),
        'created_at': generation_request.created_at.strftime('%d.%m.%Y %H:%M'),
    }

    if generation_request.status == 'completed':
        try:
            docs = generation_request.documents
            data['docx_url'] = docs.docx_file.url
            data['pptx_url'] = docs.pptx_file.url
        except GeneratedDocument.DoesNotExist:
            pass
    elif generation_request.status == 'failed':
        data['error'] = generation_request.error_message

    return JsonResponse(data)


@login_required
def history(request):
    """История генераций"""
    generations = GenerationRequest.objects.filter(
        user=request.user
    ).select_related('grade', 'subject').order_by('-created_at')

    context = {
        'generations': generations,
    }
    return render(request, 'generator/history.html', context)


@login_required
def download_docx(request, request_id):
    """Скачивание Word документа"""
    generation_request = get_object_or_404(
        GenerationRequest,
        id=request_id,
        user=request.user
    )

    if generation_request.status != 'completed':
        messages.error(request, 'Документ еще не готов')
        return redirect('generator:request_status', request_id=request_id)

    try:
        docs = generation_request.documents
        response = HttpResponse(docs.docx_file,
                                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="lesson_plan_{request_id}.docx"'
        return response
    except GeneratedDocument.DoesNotExist:
        messages.error(request, 'Файл не найден')
        return redirect('generator:history')


@login_required
def download_pptx(request, request_id):
    """Скачивание PowerPoint презентации"""
    generation_request = get_object_or_404(
        GenerationRequest,
        id=request_id,
        user=request.user
    )

    if generation_request.status != 'completed':
        messages.error(request, 'Презентация еще не готова')
        return redirect('generator:request_status', request_id=request_id)

    try:
        docs = generation_request.documents
        response = HttpResponse(docs.pptx_file,
                                content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
        response['Content-Disposition'] = f'attachment; filename="presentation_{request_id}.pptx"'
        return response
    except GeneratedDocument.DoesNotExist:
        messages.error(request, 'Файл не найден')
        return redirect('generator:history')


@require_POST
@login_required
def cancel_request(request, request_id):
    """Отмена запроса (только для pending статуса)"""
    generation_request = get_object_or_404(
        GenerationRequest,
        id=request_id,
        user=request.user,
        status='pending'
    )

    generation_request.status = 'failed'
    generation_request.error_message = 'Отменено пользователем'
    generation_request.completed_at = timezone.now()
    generation_request.save()

    messages.success(request, 'Запрос отменен')
    return redirect('generator:history')


@login_required
def get_subjects_by_grade(request):
    """API для получения предметов по классу (для AJAX)"""
    grade_id = request.GET.get('grade_id')
    if grade_id:
        subjects = Subject.objects.filter(grades__id=grade_id).values('id', 'name')
        return JsonResponse(list(subjects), safe=False)
    return JsonResponse([], safe=False)