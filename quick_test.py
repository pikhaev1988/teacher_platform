import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()
from apps.generator.services import GPTService
from django.conf import settings

print("HF TOKEN FROM DJANGO:", settings.HF_API_TOKEN)
service = GPTService()

result = service.generate_lesson_plan(
    topic="Сложение и вычитание десятичных дробей",
    grade="5",
    subject="Математика"
)

if result["success"]:
    print("УСПЕШНО")
    print(result["text"][:1000])
else:
    print("ОШИБКА:")
    print(result["error"])