import logging
import uuid

from django import test
from django.contrib.auth import get_user_model
from django.urls import reverse

from hyiptest.models import Answer, BadDomain, BadSite, HtestProgress, Question


logger = logging.getLogger(__name__)

user_model = get_user_model()


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


# HtestProgress


class HtestProgressListViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user1 = user_model.objects.create_user(
            username="testuser1", password="123"
        )
        test_user1.save()

        for _unused in range(22):
            HtestProgress.objects.create(question_in_progress=None, user=test_user1)

    def setUp(self):
        self.url = reverse("htestprogress-list")

    def test_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], "/saved-tests/")
        self.assertTemplateUsed(response, "hyiptest/htestprogress_list.html")

    def test_correct_pagination_first_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["htestprogress_list"]), 20)

    def test_correct_pagination_last_page(self):
        response = self.client.get(self.url + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["htestprogress_list"]), 2)


class HtestProgressDetailViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user1 = user_model.objects.create_user(
            username="testuser1", password="123"
        )
        test_user1.save()

        question = Question.objects.create(text="Test question")
        Answer.objects.create(text="Test answer", question=question, risk_score=69)

        progress = HtestProgress.objects.create(
            question_in_progress=None, user=test_user1
        )
        progress.selected_answers.add(question.answers.get())

    def setUp(self):
        self.progress = HtestProgress.objects.get()
        self.url = self.progress.get_absolute_url()

    def test_loads_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.request["PATH_INFO"], f"/saved-tests/{self.progress.pk}/"
        )
        self.assertTemplateUsed(response, "hyiptest/htestprogress_detail.html")


# Htest


class HtestStartViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        question = Question.objects.create(
            text="Test question?",
            description="Question for the test",
        )
        Answer.objects.create(text="Bad answer", risk_score=100, question=question)
        Answer.objects.create(text="Good answer", risk_score=0, question=question)

        test_user = user_model.objects.create_user(username="testuser", password="123")
        test_user.save()

    def test_redirects_to_login_if_not_logged_in(self):
        response = self.client.get(reverse("htest-start"))
        self.assertRedirects(response, "/accounts/login/?next=/test/")

    def test_redirects_to_test_if_logged_in(self):
        self.client.login(username="testuser", password="123")
        response = self.client.get(reverse("htest-start"))

        self.assertEqual(HtestProgress.objects.count(), 1)  # ensure only 1 was created
        progress = HtestProgress.objects.get()
        self.assertEqual(progress.question_in_progress.text, "Test question?")
        self.assertEqual(progress.user.username, "testuser")
        self.assertRedirects(response, f"/test/{progress.id}/")


class HtestQuestionViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        question1 = Question.objects.create(
            text="Test question 1?",
            description="Question for the test",
        )
        Answer.objects.create(text="Bad answer", risk_score=100, question=question1)
        Answer.objects.create(text="Good answer", risk_score=0, question=question1)

        question2 = Question.objects.create(
            text="Test question 2?",
            description="Question for the test",
        )
        answer = Answer.objects.create(
            text="Bad answer", risk_score=100, question=question2
        )
        Answer.objects.create(text="Good answer", risk_score=0, question=question2)

        test_user1 = user_model.objects.create_user(
            username="testuser1", password="123"
        )
        test_user1.save()
        test_user2 = user_model.objects.create_user(
            username="testuser2", password="456"
        )
        test_user2.save()

        HtestProgress.objects.create(question_in_progress=question1, user=test_user1)
        progress2 = HtestProgress.objects.create(
            question_in_progress=question2, user=test_user2
        )
        progress2.selected_answers.set([answer])
        HtestProgress.objects.create(question_in_progress=None, user=test_user2)

    def test_redirects_to_login_if_not_logged_in(self):
        progress = HtestProgress.objects.first()  # just get any existing
        response = self.client.get(
            reverse("htest-question", kwargs={"progress_id": progress.id})
        )
        self.assertRedirects(response, f"/accounts/login/?next=/test/{progress}/")

    def test_404_with_invalid_progress(self):
        self.client.login(username="testuser1", password="123")
        response = self.client.get(
            reverse("htest-question", kwargs={"progress_id": uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 404)

    def test_404_with_wrong_user(self):
        progress = HtestProgress.objects.get(user__username="testuser1")
        self.client.login(username="testuser2", password="456")
        response = self.client.get(
            reverse("htest-question", kwargs={"progress_id": progress.id})
        )
        self.assertEqual(response.status_code, 404)

    def test_400_with_already_finished_progress(self):
        progress = HtestProgress.objects.get(
            question_in_progress=None, user__username="testuser2"
        )
        self.client.login(username="testuser2", password="456")
        response = self.client.get(
            reverse("htest-question", kwargs={"progress_id": progress.id})
        )
        self.assertEqual(response.status_code, 400)

    def test_right_user_loads_correctly(self):
        progress = HtestProgress.objects.get(user__username="testuser1")
        self.client.login(username="testuser1", password="123")
        response = self.client.get(
            reverse("htest-question", kwargs={"progress_id": progress.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request["PATH_INFO"], f"/test/{progress.id}/")
        self.assertTemplateUsed(response, "hyiptest/htest_question.html")
        # Ensure no initial answer is selected
        self.assertDictEqual(response.context["form"].initial, {})

    def test_previously_selected_answer_is_on_form(self):
        progress = HtestProgress.objects.get(user__username="testuser1")
        initial_answer = progress.question_in_progress.answers.get(text="Bad answer")
        progress.selected_answers.set([initial_answer])

        self.client.login(username="testuser1", password="123")
        response = self.client.get(
            reverse("htest-question", kwargs={"progress_id": progress.id})
        )
        self.assertEqual(
            response.context["form"].initial["selected_answer"], initial_answer
        )

    def test_post_renders_on_invalid_form(self):
        progress = HtestProgress.objects.get(user__username="testuser1")
        self.client.login(username="testuser1", password="123")
        response = self.client.post(
            reverse("htest-question", kwargs={"progress_id": progress.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.context["form"].errors,
            {"selected_answer": ["This field is required."]},
        )

    def test_post_redirects_next_correctly(self):
        progress = HtestProgress.objects.get(user__username="testuser1")
        self.client.login(username="testuser1", password="123")
        response = self.client.post(
            reverse("htest-question", kwargs={"progress_id": progress.id}),
            {
                "selected_answer": progress.question_in_progress.answers.get(
                    text="Bad answer"
                ).id,
                "submit-next": [""],  # from self.request.POST
            },
        )

        progress = HtestProgress.objects.get(  # must get updated progress instance
            id=progress.id
        )
        next_question = Question.objects.get(text="Test question 2?")
        self.assertEqual(progress.question_in_progress, next_question)
        self.assertRedirects(
            response,
            reverse("htest-question", kwargs={"progress_id": progress.id}),
        )

    def test_post_redirects_previous_correctly(self):
        current_question = Question.objects.get(text="Test question 2?")
        progress = HtestProgress.objects.get(
            question_in_progress=current_question, user__username="testuser2"
        )
        self.client.login(username="testuser2", password="456")
        response = self.client.post(
            reverse("htest-question", kwargs={"progress_id": progress.id}),
            {
                "selected_answer": current_question.answers.get(text="Bad answer").id,
                "submit-previous": [""],
            },
        )

        progress = HtestProgress.objects.get(id=progress.id)
        previous_question = Question.objects.get(text="Test question 1?")
        self.assertEqual(progress.question_in_progress, previous_question)
        self.assertRedirects(
            response,
            reverse("htest-question", kwargs={"progress_id": progress.id}),
        )

    def test_post_400_on_missing_submit_action(self):
        progress = HtestProgress.objects.get(user__username="testuser1")
        self.client.login(username="testuser1", password="123")
        response = self.client.post(
            reverse("htest-question", kwargs={"progress_id": progress.id}),
            {
                "selected_answer": progress.question_in_progress.answers.get(
                    text="Bad answer"
                ).id,
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_post_finishes_correctly(self):
        current_question = Question.objects.get(text="Test question 2?")
        progress = HtestProgress.objects.get(
            question_in_progress=current_question, user__username="testuser2"
        )
        self.client.login(username="testuser2", password="456")
        response = self.client.post(
            reverse("htest-question", kwargs={"progress_id": progress.id}),
            {
                "selected_answer": current_question.answers.get(text="Bad answer").id,
                "submit-next": [""],
            },
        )
        self.assertRedirects(
            response, reverse("htest-result", kwargs={"progress_id": progress.id})
        )


class HtestResultViewTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user1 = user_model.objects.create_user(
            username="testuser1", password="123"
        )
        test_user1.save()

        question = Question.objects.create(text="Test question")
        bad_answer = Answer.objects.create(
            text="Bad test answer", question=question, risk_score=100
        )
        good_answer = Answer.objects.create(
            text="Good test answer", question=question, risk_score=0
        )

        bad_progress = HtestProgress.objects.create(
            question_in_progress=None, user=test_user1
        )
        good_progress = HtestProgress.objects.create(
            question_in_progress=None, user=test_user1
        )
        bad_progress.selected_answers.add(bad_answer)
        good_progress.selected_answers.add(good_answer)

    def setUp(self):
        bad_answer = Answer.objects.get(text="Bad test answer")
        good_answer = Answer.objects.get(text="Good test answer")
        self.bad_progress = HtestProgress.objects.get(
            selected_answers__in=[bad_answer]  # that has bad_answer in selected_answers
        )
        self.good_progress = HtestProgress.objects.get(
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
