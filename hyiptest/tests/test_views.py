from django import test
from django.urls import reverse

from hyiptest.models import Question


# Question


class QuestionListViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        num_questions = 22

        for question_count in range(1, num_questions + 1):
            Question.objects.create(
                text=f"Test question {question_count}?",
                description=f"Question #{question_count} for the test.",
            )

    def setUp(self):
        self.url = reverse("question-list")

    def test_view_accessible(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_url(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/questions/")

    def test_correct_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hyiptest/question_list.html")

    def test_correct_pagination(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["question_list"]), 20)

    def test_pagination_lists_all_questions(self):
        response = self.client.get(reverse("question-list") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["question_list"]), 2)


class QuestionDetailViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        Question.objects.create(
            text="Test question?",
            description="Question for the test.",
        )

    def setUp(self):
        self.question = Question.objects.get()
        self.url = self.question.get_absolute_url()

    def test_view_accessible(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_url(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.request["PATH_INFO"], f"/questions/{self.question.pk}/"
        )

    def test_correct_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hyiptest/question_detail.html")


class QuestionCreateViewTest(test.TestCase):
    def setUp(self):
        self.url = reverse("question-create")

    def test_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_url(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/questions/create/")

    def test_correct_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hyiptest/question_form.html")

    def test_correct_redirect_on_success(self):
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
        Question.objects.create(
            text="Test question?",
            description="Question for the test.",
        )

    def setUp(self):
        self.question = Question.objects.get()
        self.url = reverse("question-update", kwargs={"pk": self.question.pk})

    def test_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_url(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.request["PATH_INFO"], f"/questions/{self.question.pk}/update/"
        )

    def test_correct_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hyiptest/question_form.html")

    def test_correct_redirect_on_success(self):
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
        Question.objects.create(
            text="Test question?",
            description="Question for the test.",
        )

    def setUp(self):
        self.question = Question.objects.get()
        self.url = reverse("question-delete", kwargs={"pk": self.question.pk})

    def test_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_url(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.request["PATH_INFO"], f"/questions/{self.question.pk}/delete/"
        )

    def test_correct_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hyiptest/question_confirm_delete.html")

    def test_correct_redirect_on_success(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("question-list"))
