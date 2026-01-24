import logging

from django import test
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from hyiptest.models import Question

logger = logging.getLogger(__name__)

user_model = get_user_model()


class QuestionCreateViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user1 = user_model.objects.create_user(
            username="testuser1", password="123"
        )
        test_user1.save()
        test_user2 = user_model.objects.create_user(
            username="testuser2", password="456"
        )
        test_user2.save()

        permission = Permission.objects.get(codename="add_question")
        test_user1.user_permissions.add(permission)
        test_user1.save()

    def setUp(self):
        self.url = reverse("question-create")
        self.correct_url = "/questions/create/"

    def test_redirect_on_no_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, "/accounts/login/?next=" + self.correct_url)

    def test_403_on_wrong_user(self):
        self.client.login(username="testuser2", password="456")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_loads_correctly(self):
        self.client.login(username="testuser1", password="123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], self.correct_url)
        self.assertTemplateUsed(response, "hyiptest/question_form.html")

    def test_post_redirect_on_success(self):
        self.client.login(username="testuser1", password="123")
        response = self.client.post(
            self.url,
            {
                "text": "Test POST question?",
                "description": "Created question during test.",
            },
        )
        created_question = Question.objects.get(text="Test POST question?")
        self.assertRedirects(response, created_question.get_absolute_url())


class QuestionUpdateViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user1 = user_model.objects.create_user(
            username="testuser1", password="123"
        )
        test_user1.save()
        test_user2 = user_model.objects.create_user(
            username="testuser2", password="456"
        )
        test_user2.save()

        permission = Permission.objects.get(codename="change_question")
        test_user1.user_permissions.add(permission)
        test_user1.save()

        Question.objects.create(
            text="Test question?",
            description="Question for the test.",
        )

    def setUp(self):
        self.question = Question.objects.get()
        self.url = reverse("question-update", kwargs={"pk": self.question.pk})
        self.correct_url = f"/questions/{self.question.pk}/update/"

    def test_redirect_on_no_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, "/accounts/login/?next=" + self.correct_url)

    def test_403_on_wrong_user(self):
        self.client.login(username="testuser2", password="456")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_loads_correctly(self):
        self.client.login(username="testuser1", password="123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], self.correct_url)
        self.assertTemplateUsed(response, "hyiptest/question_form.html")

    def test_post_redirect_on_success(self):
        self.client.login(username="testuser1", password="123")
        response = self.client.post(
            self.url,
            {
                "text": "Updated test question?",
                "description": "Updated question during test.",
            },
        )
        updated_question = Question.objects.get(text="Updated test question?")
        self.assertRedirects(response, updated_question.get_absolute_url())


class QuestionDeleteViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user1 = user_model.objects.create_user(
            username="testuser1", password="123"
        )
        test_user1.save()
        test_user2 = user_model.objects.create_user(
            username="testuser2", password="456"
        )
        test_user2.save()

        permission = Permission.objects.get(codename="delete_question")
        test_user1.user_permissions.add(permission)
        test_user1.save()

        Question.objects.create(
            text="Test question?",
            description="Question for the test.",
        )

    def setUp(self):
        self.question = Question.objects.get()
        self.url = reverse("question-delete", kwargs={"pk": self.question.pk})
        self.correct_url = f"/questions/{self.question.pk}/delete/"

    def test_redirect_on_no_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, "/accounts/login/?next=" + self.correct_url)

    def test_403_on_wrong_user(self):
        self.client.login(username="testuser2", password="456")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_loads_correctly(self):
        self.client.login(username="testuser1", password="123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], self.correct_url)
        self.assertTemplateUsed(response, "hyiptest/question_confirm_delete.html")

    def test_post_redirect_on_success(self):
        self.client.login(username="testuser1", password="123")
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("question-list"))
