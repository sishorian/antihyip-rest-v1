import uuid

from django import test
from django.urls import reverse

from hyiptest.models import Answer, BadDomain, BadSite, HtestSnapshot, Question


class HomePageViewTest(test.TestCase):
    def setUp(self):
        self.url = reverse("home")

    def test_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/")
        self.assertTemplateUsed(response, "home.html")


# BadSite


class BadSiteListViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        total_sites = 22

        for i in range(1, total_sites + 1):
            BadSite.objects.create(name=f"Bad site {i}", bad_type="Unittest")

    def setUp(self):
        self.url = reverse("badsite-list")

    def test_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/badsites/")
        self.assertTemplateUsed(response, "hyiptest/badsite_list.html")

    def test_correct_pagination_first_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["badsite_list"]), 20)

    def test_correct_pagination_last_page(self):
        response = self.client.get(self.url + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["badsite_list"]), 2)


class BadSiteDetailViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        BadSite.objects.create(name="Test Zero", bad_type="Unittest")

    def setUp(self):
        self.badsite = BadSite.objects.get()
        self.url = self.badsite.get_absolute_url()

    def test_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], f"/badsites/{self.badsite.pk}/")
        self.assertTemplateUsed(response, "hyiptest/badsite_detail.html")


# Search Domain


class SearchDomainViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        badsite = BadSite.objects.create(name="Test Zero", bad_type="Unittest")
        BadDomain.objects.create(name="test-zero.com", site=badsite)

    def setUp(self):
        self.badsite = BadSite.objects.get()
        self.url = reverse("search-domain")

    def test_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/search-domain/")
        self.assertTemplateUsed(response, "hyiptest/search_domain.html")

    def test_match_on_existing(self):
        response = self.client.get(self.url, {"q": "test-zero.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["found_badsite"].name, "Test Zero")

    def test_no_match_on_unknown(self):
        response = self.client.get(self.url, {"q": "blah-one.com"})
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["found_badsite"])


# Question


class QuestionListViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        total_questions = 22

        for i in range(1, total_questions + 1):
            Question.objects.create(
                text=f"Test question {i}?",
                description=f"Question #{i} for the test.",
            )

    def setUp(self):
        self.url = reverse("question-list")

    def test_loads_correctly(self):
        # def test_view_accessible(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # def test_correct_url(self):
        self.assertEqual(response.request["PATH_INFO"], "/questions/")
        # def test_correct_template(self):
        self.assertTemplateUsed(response, "hyiptest/question_list.html")

    def test_correct_pagination_first_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["question_list"]), 20)

    def test_correct_pagination_last_page(self):
        response = self.client.get(self.url + "?page=2")
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

    def test_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.request["PATH_INFO"], f"/questions/{self.question.pk}/"
        )
        self.assertTemplateUsed(response, "hyiptest/question_detail.html")


class QuestionCreateViewTest(test.TestCase):
    def setUp(self):
        self.url = reverse("question-create")

    def test_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/questions/create/")
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

    def test_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.request["PATH_INFO"], f"/questions/{self.question.pk}/update/"
        )
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

    def test_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.request["PATH_INFO"], f"/questions/{self.question.pk}/delete/"
        )
        self.assertTemplateUsed(response, "hyiptest/question_confirm_delete.html")

    def test_correct_redirect_on_success(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("question-list"))


# HtestSnapshot


class HtestSnapshotListViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        total_snapshots = 22

        for i in range(1, total_snapshots + 1):
            HtestSnapshot.objects.create()

    def setUp(self):
        self.url = reverse("htestsnapshot-list")

    def test_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/saved-tests/")
        self.assertTemplateUsed(response, "hyiptest/htestsnapshot_list.html")

    def test_correct_pagination_first_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["htestsnapshot_list"]), 20)

    def test_correct_pagination_last_page(self):
        response = self.client.get(self.url + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["htestsnapshot_list"]), 2)


class HtestSnapshotDetailViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        question = Question.objects.create(text="Test question")
        Answer.objects.create(text="Test answer", question=question, risk_score=69)
        snapshot = HtestSnapshot.objects.create(question_in_progress=None)
        snapshot.selected_answers.add(Answer.objects.get(text="Test answer"))

    def setUp(self):
        self.snapshot = HtestSnapshot.objects.get()
        self.url = self.snapshot.get_absolute_url()

    def test_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.request["PATH_INFO"], f"/saved-tests/{self.snapshot.pk}/"
        )
        self.assertTemplateUsed(response, "hyiptest/htestsnapshot_detail.html")


# Htest


class HtestQuestionViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        question1 = Question.objects.create(
            text="Test question 1?",
            description="Question for the test.",
        )
        Answer.objects.create(text="Bad answer", risk_score=100, question=question1)
        Answer.objects.create(text="Good answer", risk_score=0, question=question1)

        question2 = Question.objects.create(
            text="Test question 2?",
            description="Question for the test.",
        )
        Answer.objects.create(text="Bad answer", risk_score=100, question=question2)
        Answer.objects.create(text="Good answer", risk_score=0, question=question2)

    def test_without_progress_loads_correctly(self):
        response = self.client.get(reverse("htest-question"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/test/")
        self.assertTemplateUsed(response, "hyiptest/htest_question.html")

    def test_with_progress_loads_correctly(self):
        question = Question.objects.get(text="Test question 1?")
        progress = HtestSnapshot.objects.create(question_in_progress=question)
        response = self.client.get(
            reverse("htest-question", kwargs={"progress_id": progress.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], f"/test/{progress.id}/")
        self.assertTemplateUsed(response, "hyiptest/htest_question.html")

    def test_404_with_invalid_progress(self):
        response = self.client.get(
            reverse("htest-question", kwargs={"progress_id": uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 404)

    def test_400_with_finished_progress(self):
        finished_progress = HtestSnapshot.objects.create(question_in_progress=None)
        response = self.client.get(
            reverse("htest-question", kwargs={"progress_id": finished_progress.id})
        )
        self.assertEqual(response.status_code, 400)

    def test_post_loads_correctly(self):
        # New progress because the view will change it
        current_question = Question.objects.get(text="Test question 1?")
        new_progress = HtestSnapshot.objects.create(
            question_in_progress=current_question
        )
        response = self.client.post(
            reverse("htest-question", kwargs={"progress_id": new_progress.id}),
            {
                "selected_answer": Answer.objects.get(
                    text="Bad answer", question=current_question
                ).id
            },
        )
        self.assertRedirects(
            response,
            reverse("htest-question", kwargs={"progress_id": new_progress.id}),
        )

    def test_post_finishes_correctly(self):
        # New progress because the view will change it
        current_question = Question.objects.get(text="Test question 2?")
        new_progress = HtestSnapshot.objects.create(
            question_in_progress=current_question
        )
        response = self.client.post(
            reverse("htest-question", kwargs={"progress_id": new_progress.id}),
            {
                "selected_answer": Answer.objects.get(
                    text="Good answer", question=current_question
                ).id
            },
        )
        self.assertRedirects(
            response, reverse("htest-result", kwargs={"progress_id": new_progress.id})
        )


class HtestResultViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        question = Question.objects.create(text="Test question")
        Answer.objects.create(text="Bad test answer", question=question, risk_score=100)
        Answer.objects.create(text="Good test answer", question=question, risk_score=0)
        bad_progress = HtestSnapshot.objects.create(question_in_progress=None)
        good_progress = HtestSnapshot.objects.create(question_in_progress=None)
        bad_progress.selected_answers.add(Answer.objects.get(text="Bad test answer"))
        good_progress.selected_answers.add(Answer.objects.get(text="Good test answer"))

    def setUp(self):
        bad_answer = Answer.objects.get(text="Bad test answer")
        good_answer = Answer.objects.get(text="Good test answer")
        self.bad_progress = HtestSnapshot.objects.get(
            selected_answers__in=[bad_answer]  # that has bad_answer in selected_answers
        )
        self.good_progress = HtestSnapshot.objects.get(
            selected_answers__in=[good_answer]
        )

    def test_bad_result_loads_correctly(self):
        response = self.client.get(
            reverse("htest-result", kwargs={"progress_id": self.bad_progress.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.request["PATH_INFO"], f"/test/{self.bad_progress.id}/result/"
        )
        self.assertTemplateUsed(response, "hyiptest/htest_result.html")
        self.assertTrue(response.context["result_is_bad"])

    def test_good_result_loads_correctly(self):
        response = self.client.get(
            reverse("htest-result", kwargs={"progress_id": self.good_progress.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.request["PATH_INFO"], f"/test/{self.good_progress.id}/result/"
        )
        self.assertTemplateUsed(response, "hyiptest/htest_result.html")
        self.assertFalse(response.context["result_is_bad"])
