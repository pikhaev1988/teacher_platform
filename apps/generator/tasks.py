#apps/generator/taks
from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone
import logging
from .models import GenerationRequest, GeneratedDocument
from .services import GPTService, DocumentGenerator

logger = logging.getLogger(__name__)


@shared_task
def generate_materials_task(request_id):
    """
    Celery задача для генерации материалов
    """
    try:
        request = GenerationRequest.objects.get(id=request_id)
    except GenerationRequest.DoesNotExist:
        logger.error(f"GenerationRequest with id {request_id} not found")
        return

    # Обновляем статус
    # Обновляем статус
    request.status = 'processing'
    request.save()

    # Инициализируем сервисы
    gpt_service = GPTService()
    doc_generator = DocumentGenerator()

    # Генерируем план через GPT
    result = gpt_service.generate_lesson_plan(
        topic=request.topic,
        grade=request.grade,
        subject=request.subject
    )

    # Обновляем информацию о токенах


    if not result['success']:
        request.status = 'failed'
        request.error_message = result['error']
        request.completed_at = timezone.now()
        request.save()
        logger.error(f"Generation failed for request {request_id}: {result['error']}")
        return

    request.prompt_tokens = result['prompt_tokens']
    request.completion_tokens = result['completion_tokens']

    try:
        # Генерируем Word документ
        docx_stream = doc_generator.create_docx_from_markdown(
            result['text'],
            request.topic
        )

        # Генерируем PowerPoint презентацию
        pptx_stream = doc_generator.create_pptx_from_markdown(
            result['text'],
            request.topic
        )

        # Создаем и сохраняем документы
        documents = GeneratedDocument.objects.create(
            request=request,
            docx_text=result['text']
        )

        # Сохраняем файлы
        docx_filename = f"lesson_plan_{request.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.docx"
        documents.docx_file.save(
            docx_filename,
            ContentFile(docx_stream.getvalue())
        )

        pptx_filename = f"presentation_{request.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pptx"
        documents.pptx_file.save(
            pptx_filename,
            ContentFile(pptx_stream.getvalue())
        )

        # Обновляем статус запроса
        request.status = 'completed'
        request.completed_at = timezone.now()
        request.save()

        # Увеличиваем счетчик генераций у пользователя
        user = request.user
        user.total_generations += 1
        user.save()

        logger.info(f"Successfully generated materials for request {request_id}")

    except Exception as e:
        request.status = 'failed'
        request.error_message = str(e)
        request.completed_at = timezone.now()
        request.save()
        logger.exception(f"Error saving generated files for request {request_id}: {e}")