#apps/generator/models
from django.db import models
from django.conf import settings


class Subject(models.Model):
    """Предмет"""
    name = models.CharField(max_length=100, verbose_name='Название')
    grades = models.ManyToManyField('Grade', verbose_name='Классы')

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

    def __str__(self):
        return self.name


class Grade(models.Model):
    """Класс"""
    number = models.PositiveSmallIntegerField(unique=True, verbose_name='Класс')

    class Meta:
        verbose_name = 'Класс'
        verbose_name_plural = 'Классы'
        ordering = ['number']

    def __str__(self):
        return f'{self.number} класс'


class GenerationRequest(models.Model):
    """Запрос на генерацию"""
    STATUS_CHOICES = [
        ('pending', 'В очереди'),
        ('processing', 'Генерируется'),
        ('completed', 'Готово'),
        ('failed', 'Ошибка'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='generation_requests',
                             verbose_name='Пользователь')
    topic = models.CharField(max_length=500, verbose_name='Тема урока')
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, verbose_name='Класс')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, verbose_name='Предмет')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')

    prompt_tokens = models.PositiveIntegerField(default=0, verbose_name='Токенов в запросе')
    completion_tokens = models.PositiveIntegerField(default=0, verbose_name='Токенов в ответе')

    error_message = models.TextField(blank=True, verbose_name='Сообщение об ошибке')

    class Meta:
        verbose_name = 'Запрос на генерацию'
        verbose_name_plural = 'Запросы на генерацию'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.topic} - {self.grade} ({self.get_status_display()})'


class GeneratedDocument(models.Model):
    """Сгенерированный документ"""
    request = models.OneToOneField(GenerationRequest, on_delete=models.CASCADE, related_name='documents',
                                   verbose_name='Запрос')
    docx_file = models.FileField(upload_to='generated/docx/%Y/%m/%d/', verbose_name='Word документ')
    pptx_file = models.FileField(upload_to='generated/pptx/%Y/%m/%d/', verbose_name='PowerPoint презентация')
    docx_text = models.TextField(verbose_name='Текст документа')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Сгенерированный документ'
        verbose_name_plural = 'Сгенерированные документы'

    def __str__(self):
        return f'Документы для запроса #{self.request.id}'