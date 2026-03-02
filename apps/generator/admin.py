#apps/generator/admin
from django.contrib import admin
from .models import Subject, Grade, GenerationRequest, GeneratedDocument


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('grades',)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('number',)


class GeneratedDocumentInline(admin.StackedInline):
    model = GeneratedDocument
    can_delete = False


@admin.register(GenerationRequest)
class GenerationRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'topic', 'grade', 'subject', 'status', 'created_at')
    list_filter = ('status', 'grade', 'subject')
    search_fields = ('topic', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'completed_at', 'prompt_tokens', 'completion_tokens')
    inlines = [GeneratedDocumentInline]

    fieldsets = (
        ('Информация о запросе', {
            'fields': ('user', 'topic', 'grade', 'subject', 'status')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'completed_at')
        }),
        ('Статистика API', {
            'fields': ('prompt_tokens', 'completion_tokens')
        }),
        ('Ошибки', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )


@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = ('request', 'created_at')
    readonly_fields = ('created_at',)