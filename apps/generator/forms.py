#apps/generator/forms
from django import forms
from .models import GenerationRequest, Subject, Grade


class GenerationRequestForm(forms.ModelForm):
    """Форма запроса на генерацию"""

    class Meta:
        model = GenerationRequest
        fields = ['topic', 'grade', 'subject']
        widgets = {
            'topic': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите тему урока...'
            }),
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'topic': 'Тема урока',
            'grade': 'Класс',
            'subject': 'Предмет',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем предметы по выбранному классу (будет обновляться через AJAX)
        self.fields['subject'].queryset = Subject.objects.all()