import logging

from django.core.exceptions import BadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic

from hyiptest.forms import SearchDomainForm, SelectAnswerForm
from hyiptest.models import BadDomain, BadSite, HtestSnapshot, Question


logger = logging.getLogger(__name__)


# Home page


class HomePageView(generic.TemplateView):
    template_name = "home.html"


# BadSite


class BadSiteListView(generic.ListView):
    model = BadSite
    paginate_by = 20


class BadSiteDetailView(generic.DetailView):
    model = BadSite


# Search domain


class SearchDomainView(generic.TemplateView):
    """
    View for searching domain in the fraud database.
    """

    template_name = "hyiptest/search_domain.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # New search form requested
        if "q" not in self.request.GET:
            context["form"] = SearchDomainForm()
            context["executed_query"] = None  # just to be explicit
            return context

        # Search submitted
        context["form"] = SearchDomainForm(self.request.GET)
        if not context["form"].is_valid():
            context["executed_query"] = None
            return context

        # Search executed
        context["executed_query"] = self.request.GET["q"]
        try:
            context["found_badsite"] = BadDomain.objects.get(
                name=context["executed_query"]
            ).site
        except BadDomain.DoesNotExist:
            context["found_badsite"] = None  # just to be explicit
        return context


# Question


class QuestionListView(generic.ListView):
    model = Question
    paginate_by = 20


class QuestionDetailView(generic.DetailView):
    model = Question


class QuestionCreateView(generic.CreateView):
    model = Question
    fields = ["text", "description"]


class QuestionUpdateView(generic.UpdateView):
    model = Question
    fields = ["text", "description"]


class QuestionDeleteView(generic.DeleteView):
    model = Question
    success_url = reverse_lazy("question-list")


# HtestSnapshot


class HtestSnapshotListView(generic.ListView):
    model = HtestSnapshot
    paginate_by = 20


class HtestSnapshotDetailView(generic.DetailView):
    model = HtestSnapshot


# HyipTest (Htest)
# Just `test_` can be confused with unittest


class HtestQuestionView(generic.View):
    """
    View for asking user one question from the test.
    """

    def setup(self, request, *args, **kwargs):
        if kwargs["progress_id"] is None:  # new test created
            # Delete all previous incomplete tests, for now
            HtestSnapshot.objects.filter(question_in_progress__isnull=False).delete()

            kwargs["current_question"] = Question.objects.order_by("created_at").first()
            kwargs["saved_progress"] = HtestSnapshot.objects.create(
                question_in_progress=kwargs["current_question"]
            )
        else:  # test in progress or resumed
            kwargs["saved_progress"] = get_object_or_404(
                HtestSnapshot, id=kwargs["progress_id"]
            )
            kwargs["current_question"] = kwargs["saved_progress"].question_in_progress
            if kwargs["current_question"] is None:
                raise BadRequest("Attempt to resume a test that is already finised")

        # Previously created question, should be None on the first question
        kwargs["previous_question"] = (
            Question.objects.filter(
                created_at__lt=kwargs["current_question"].created_at
            )
            .order_by("-created_at")
            .first()
        )
        # Later created question
        kwargs["next_question"] = (
            Question.objects.filter(
                created_at__gt=kwargs["current_question"].created_at
            )
            .order_by("created_at")
            .first()
        )
        # Answers belonging to current_question
        kwargs["displayed_answers"] = kwargs["current_question"].answers.all()

        kwargs["current_question_position"] = Question.objects.filter(
            # lt -> 0..(n-1), lte -> 1..n
            created_at__lte=kwargs["current_question"].created_at
        ).count()
        kwargs["total_questions"] = Question.objects.count()

        # request -> self.request; args -> self.args; kwargs -> self.kwargs
        super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # setup() kwargs don't get passed here, only self.kwargs
        self.kwargs["form"] = SelectAnswerForm(
            answer_queryset=self.kwargs["displayed_answers"]
        )
        return render(request, "hyiptest/htest_question.html", self.kwargs)

    def post(self, request, *args, **kwargs):
        self.kwargs["form"] = SelectAnswerForm(
            request.POST, answer_queryset=self.kwargs["displayed_answers"]
        )
        if not self.kwargs["form"].is_valid():
            return render(request, "hyiptest/htest_question.html", self.kwargs)

        # If a new answer "contradicts" previous, update it
        # Remove `ORDER BY` SQL because it's incompatible with unions in SQLite
        selected_before = (
            self.kwargs["displayed_answers"]
            .order_by()
            .intersection(
                self.kwargs["saved_progress"].selected_answers.all().order_by()
            )
        )
        if selected_before.exists():
            logger.debug("Removing previous contradicting answers: %s", selected_before)
            self.kwargs["saved_progress"].selected_answers.remove(*selected_before)

        self.kwargs["saved_progress"].selected_answers.add(
            self.kwargs["form"].cleaned_data["selected_answer"]
        )

        if (
            "submit-previous" in request.POST
            and self.kwargs["previous_question"] is None
        ):
            # Just refresh form, for now
            return render(request, "hyiptest/htest_question.html", self.kwargs)
        if "submit-previous" in request.POST:
            self.kwargs["saved_progress"].question_in_progress = self.kwargs[
                "previous_question"
            ]
            self.kwargs["saved_progress"].save()
            return redirect(
                "htest-question", progress_id=self.kwargs["saved_progress"].id
            )

        if "submit-next" in request.POST and self.kwargs["next_question"] is None:
            self.kwargs["saved_progress"].question_in_progress = None
            self.kwargs["saved_progress"].save()
            return redirect(
                "htest-result", progress_id=self.kwargs["saved_progress"].id
            )
        if "submit-next" in request.POST:
            self.kwargs["saved_progress"].question_in_progress = self.kwargs[
                "next_question"
            ]
            self.kwargs["saved_progress"].save()
            return redirect(
                "htest-question", progress_id=self.kwargs["saved_progress"].id
            )

        raise BadRequest("Form submitted but neither action was triggered")


class HtestResultView(generic.TemplateView):
    template_name = "hyiptest/htest_result.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        def result_is_bad(result):
            return result >= 100

        context["result_is_bad"] = result_is_bad(
            get_object_or_404(
                HtestSnapshot, id=self.kwargs["progress_id"]
            ).get_total_risk_score()
        )
        return context
