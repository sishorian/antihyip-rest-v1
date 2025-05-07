from django import test
from django.db.utils import IntegrityError

from hyiptest.models import Question


class QuestionModelTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        Question.objects.create(
            text="Is it a question for QuestionModelTest?",
            description="Question for QuestionModelTest.",
        )

    def test_object_name_is_text(self):
        """
        Ensure the object name is correct.
        """
        question = Question.objects.get()
        self.assertEqual(str(question), question.text)

    def test_get_absolute_url(self):
        """
        Ensure the object's get_absolute_url() is working correctly.
        """
        question = Question.objects.get()
        self.assertEqual(question.get_absolute_url(), f"/questions/{question.pk}/")

    # 'id' field

    def test_id_label(self):
        """
        Ensure 'id' field has correct label.
        """
        question = Question.objects.get()
        field_label = question._meta.get_field("id").verbose_name
        self.assertEqual(field_label, "ID")

    # 'text' field

    def test_text_label(self):
        """
        Ensure 'text' field has correct label.
        """
        question = Question.objects.get()
        field_label = question._meta.get_field("text").verbose_name
        self.assertEqual(field_label, "text")

    def test_text_max_length(self):
        """
        Ensure 'text' field has correct max_length.
        """
        question = Question.objects.get()
        max_length = question._meta.get_field("text").max_length
        self.assertEqual(max_length, 100)

    def test_text_unique_ci(self):
        """
        Ensure you can't create object with the same 'text' field.

        Even if the letters have different case.
        """
        with self.assertRaises(IntegrityError):
            Question.objects.create(text="iS IT a qUEstion fOr QuESTIonModelTest?")

    # 'description' field

    def test_description_label(self):
        """
        Ensure 'description' field has correct label.
        """
        question = Question.objects.get()
        field_label = question._meta.get_field("description").verbose_name
        self.assertEqual(field_label, "description")

    def test_description_max_length(self):
        """
        Ensure 'description' field has correct max_length.
        """
        question = Question.objects.get()
        max_length = question._meta.get_field("description").max_length
        self.assertEqual(max_length, 200)
