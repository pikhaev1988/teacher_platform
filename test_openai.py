import os
import django
from pathlib import Path

# Настройка Django окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.generator.services import GPTService, DocumentGenerator
from apps.generator.models import Grade, Subject


def test_openai_connection():
    """Тест подключения к OpenAI"""
    print("🔍 Тестируем подключение к OpenAI...")

    service = GPTService()

    # Простой тестовый запрос
    try:
        response = service.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты - полезный ассистент."},
                {"role": "user", "content": "Скажи 'Привет, мир!' на русском языке"}
            ],
            max_tokens=50
        )

        print("✅ Подключение к OpenAI успешно!")
        print(f"Ответ: {response.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False


def test_generate_lesson_plan():
    """Тест генерации поурочного плана"""
    print("\n🔍 Тестируем генерацию поурочного плана...")

    service = GPTService()

    # Тестовые данные
    topic = "Сложение и вычитание десятичных дробей"
    grade = "5"
    subject = "Математика"

    result = service.generate_lesson_plan(topic, grade, subject)

    if result['success']:
        print("✅ Генерация плана успешна!")
        print(f"📊 Использовано токенов: {result['prompt_tokens'] + result['completion_tokens']}")
        print(f"📝 Сгенерированный текст (первые 500 символов):")
        print("-" * 50)
        print(result['text'][:500])
        print("-" * 50)
        return result['text']
    else:
        print(f"❌ Ошибка генерации: {result['error']}")
        return None


def test_document_generation(text):
    """Тест создания документов"""
    if not text:
        print("\n❌ Нет текста для создания документов")
        return

    print("\n🔍 Тестируем создание документов...")

    doc_generator = DocumentGenerator()

    try:
        # Создаем Word документ
        docx_stream = doc_generator.create_docx_from_markdown(text, "Тестовый урок")
        print("✅ Word документ создан успешно")

        # Создаем PowerPoint презентацию
        pptx_stream = doc_generator.create_pptx_from_markdown(text, "Тестовый урок")
        print("✅ PowerPoint презентация создана успешно")

        # Сохраняем тестовые файлы
        with open('test_lesson.docx', 'wb') as f:
            f.write(docx_stream.getvalue())
        print("💾 Файл сохранен: test_lesson.docx")

        with open('test_lesson.pptx', 'wb') as f:
            f.write(pptx_stream.getvalue())
        print("💾 Файл сохранен: test_lesson.pptx")

    except Exception as e:
        print(f"❌ Ошибка создания документов: {e}")


def test_multiple_topics():
    """Тест генерации разных тем"""
    print("\n🔍 Тестируем генерацию разных тем...")

    test_cases = [
        {"topic": "Правописание безударных гласных в корне", "grade": "3", "subject": "Русский язык"},
        {"topic": "Теорема Пифагора", "grade": "8", "subject": "Геометрия"},
        {"topic": "Фотосинтез", "grade": "6", "subject": "Биология"},
    ]

    service = GPTService()

    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Тест {i}: {case['topic']}")
        result = service.generate_lesson_plan(
            case['topic'],
            case['grade'],
            case['subject']
        )

        if result['success']:
            print(f"  ✅ Успешно (токенов: {result['prompt_tokens'] + result['completion_tokens']})")
        else:
            print(f"  ❌ Ошибка: {result['error']}")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ OPENAI ИНТЕГРАЦИИ")
    print("=" * 60)

    # Шаг 1: Проверка подключения
    if test_openai_connection():
        # Шаг 2: Генерация плана
        text = test_generate_lesson_plan()

        # Шаг 3: Создание документов
        test_document_generation(text)

        # Шаг 4: Тест разных тем
        test_multiple_topics()

    print("\n" + "=" * 60)
    print("✅ Тестирование завершено!")