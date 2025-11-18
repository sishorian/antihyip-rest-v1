from django import test

from hyiptest.forms import SearchDomainForm, SelectAnswerForm
from hyiptest.models import Answer, Question


class SearchDomainFormTest(test.SimpleTestCase):
    def test_domain_valid(self):
        form = SearchDomainForm(data={"q": "test123.com"})
        self.assertTrue(form.is_valid())

    def test_domain_invalid(self):
        form = SearchDomainForm(data={"q": "test123com"})
        self.assertFalse(form.is_valid())

    def test_domain_not_lower_case(self):
        form = SearchDomainForm(data={"q": "tEst123.com"})
        self.assertFalse(form.is_valid())

    def test_domain_too_short(self):
        form = SearchDomainForm(data={"q": "t.co"})
        self.assertFalse(form.is_valid())

    def test_domain_too_long(self):
        form = SearchDomainForm(data={"q": ("do" * 25 + "." + "co" * 25)})
        self.assertFalse(form.is_valid())


class SelectAnswerFormTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        question = Question.objects.create(
            text="Test question?",
            description="Question for the test.",
        )
        Answer.objects.create(text="Bad answer", risk_score=100, question=question)
        Answer.objects.create(text="Good answer", risk_score=0, question=question)

    def test_answer_selected(self):
        form = SelectAnswerForm(
            data={"selected_answer": Answer.objects.get(text="Bad answer")},
            question_obj=Question.objects.get(),
        )
        self.assertTrue(form.is_valid())

    def test_answer_not_selected(self):
        form = SelectAnswerForm(
            data={"selected_answer": None}, question_obj=Question.objects.get()
        )
        self.assertFalse(form.is_valid())
