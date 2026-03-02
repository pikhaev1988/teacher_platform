#apps/generator/managemads/seed_grades_subjects.py
from django.core.management.base import BaseCommand
from apps.generator.models import Grade, Subject


class Command(BaseCommand):
    help = 'Заполняет базу данных начальными классами и предметами'

    def handle(self, *args, **options):
        # Создаем классы
        grades = []
        for i in range(1, 12):
            grade, created = Grade.objects.get_or_create(number=i)
            if created:
                grades.append(grade)
                self.stdout.write(self.style.SUCCESS(f'Создан класс: {i}'))

        # Создаем предметы и привязываем к классам
        subjects_data = [
            {
                'name': 'Русский язык',
                'grades': list(range(1, 12))
            },
            {
                'name': 'Литература',
                'grades': list(range(5, 12))
            },
            {
                'name': 'Математика',
                'grades': list(range(1, 7))
            },
            {
                'name': 'Алгебра',
                'grades': list(range(7, 12))
            },
            {
                'name': 'Геометрия',
                'grades': list(range(7, 12))
            },
            {
                'name': 'История',
                'grades': list(range(5, 12))
            },
            {
                'name': 'Обществознание',
                'grades': list(range(6, 12))
            },
            {
                'name': 'Физика',
                'grades': list(range(7, 12))
            },
            {
                'name': 'Химия',
                'grades': list(range(8, 12))
            },
            {
                'name': 'Биология',
                'grades': list(range(5, 12))
            },
            {
                'name': 'География',
                'grades': list(range(6, 12))
            },
            {
                'name': 'Английский язык',
                'grades': list(range(2, 12))
            },
            {
                'name': 'Информатика',
                'grades': list(range(7, 12))
            },
            {
                'name': 'Физкультура',
                'grades': list(range(1, 12))
            },
            {
                'name': 'ОБЖ',
                'grades': list(range(8, 12))
            },
        ]

        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(name=subject_data['name'])
            if created:
                for grade_num in subject_data['grades']:
                    grade = Grade.objects.get(number=grade_num)
                    subject.grades.add(grade)
                self.stdout.write(self.style.SUCCESS(f'Создан предмет: {subject_data["name"]}'))