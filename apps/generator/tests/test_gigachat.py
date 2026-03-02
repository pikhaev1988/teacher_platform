from django.test import TestCase
from apps.generator.services import GPTService


class GigaChatTest(TestCase):

    def test_generate_lesson_plan(self):
        service = GPTService()

        result = service.generate_lesson_plan(
            topic="Имена существительные единственного и множественного числа",
            grade="5",
            subject="Русский язык"
        )

        print("\n=== RESULT ===")
        print(result)

        self.assertTrue(result["success"])
        self.assertIn("тип урока", result["text"].lower())