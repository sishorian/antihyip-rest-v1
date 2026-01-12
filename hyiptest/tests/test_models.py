from django import test
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from hyiptest.models import Answer, BadDomain, BadSite, HtestProgress, Question


user_model = get_user_model()


# See QuestionModelTest for a more verbose example for a model test class
# Don't do 'boring' tests for other models


class BadSiteModelTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        BadSite.objects.create(
            name="Test One",
            bad_type="test",
        )

    def test_name_lower_unique_constraint(self):
        """
        Ensure you can't create object with the same 'name' field.

        Even if the letters have different case.
        """
        with self.assertRaises(IntegrityError):
            BadSite.objects.create(name="TesT oNe")


class BadDomainModelTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        badsite = BadSite.objects.create(
            name="Test One",
            bad_type="test",
        )
        BadDomain.objects.create(
            name="testone.test",
            site=badsite,
        )

    def setUp(self):
        self.badsite = BadSite.objects.get(name="Test One")

    def test_name_domain_validator(self):
        """
        Ensure that 'name' field accepts only domains.
        """
        baddomain = BadDomain(name="testone", site=self.badsite)
        with self.assertRaises(ValidationError):
            baddomain.full_clean()

    def test_name_converted_lower(self):
        """
        Ensure that 'name' field is converted to lowercase on clean().
        """
        name = "tEStonE.cOm"
        domain = BadDomain(name=name, site=self.badsite)
        domain.full_clean()
        self.assertEqual(domain.name, name.lower())

    def test_name_lower_constraint(self):
        """
        Ensure you can't create object if 'name' field is not lowercase.

        For cases where clean() is not run, e.g. when creating from shell.
        """
        with self.assertRaises(IntegrityError):
            BadDomain.objects.create(name="testoNE.tESt")
            # Btw, save() is not run here:
            # BadDomain.objects.filter(name="testone.test").update(name="testoNE.tESt")

    def test_site_related_name_domains(self):
        """
        Ensure the related object has correct backwards-relation Manager name.
        """
        field = self.badsite._meta.get_field("domains")
        self.assertEqual(field.related_name, "domains")


# Example test class for a model
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

    def test_text_lower_unique_constraint(self):
        """
        Ensure you can't create object with the same 'text' field.

        Even if the letters have different case.
        """
        with self.assertRaises(IntegrityError):
            Question.objects.create(text="iS IT a qUEstion fOr QuestionModelTest?")

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


class AnswerModelTest(test.TestCase):
    def test_error_on_null_question(self):
        """
        Ensure Answer with no `question` can't be created.
        """
        with self.assertRaises(IntegrityError):
            Answer.objects.create(
                text="Answer with no question", question=None, risk_score=69
            )

    def test_error_on_null_risk_score(self):
        """
        Ensure Answer with no `risk_score` can't be created.
        """
        question = Question.objects.create(text="Test Question")
        with self.assertRaises(IntegrityError):
            Answer.objects.create(text="Answer with no question", question=question)


class HtestProgressModelTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user1 = user_model.objects.create_user(
            username="testuser1", password="123"
        )
        test_user1.save()

        question1 = Question.objects.create(text="Test Question 1")
        question2 = Question.objects.create(text="Test Question 2")
        answer_q1 = Answer.objects.create(
            text="Answer q1", risk_score=33, question=question1
        )
        answer_q2 = Answer.objects.create(
            text="Answer q2", risk_score=66, question=question2
        )

        progress = HtestProgress.objects.create(
            question_in_progress=None, user=test_user1
        )
        progress.selected_answers.set([answer_q1, answer_q2])

    def test_get_total_risk_score(self):
        """
        Ensure get_total_risk_score() method works correctly.
        """
        progress = HtestProgress.objects.get()
        self.assertEqual(progress.get_total_risk_score(), 99)
