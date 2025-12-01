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


# htest - short for hyiptest
# Just `test` can be confused with unittest.
def htest_question(request, progress_id=None):
    """
    View function for asking user one question from the test.
    """

    if progress_id is None:  # user takes new test
        current_question = Question.objects.order_by("created_at").first()
        previous_question = None  # shouldn't be any questions created before the first
        # Delete all previous incomplete tests, for now
        HtestSnapshot.objects.filter(question_in_progress__isnull=False).delete()
        # New save
        saved_progress = HtestSnapshot.objects.create(
            question_in_progress=current_question
        )
    else:
        saved_progress = get_object_or_404(HtestSnapshot, id=progress_id)
        if saved_progress.question_in_progress is None:
            raise BadRequest("Attempt to resume a test that is already finised")
        current_question = Question.objects.get(
            id=saved_progress.question_in_progress.id
        )
        previous_question = (  # previously created question
            Question.objects.filter(created_at__lt=current_question.created_at)
            .order_by("-created_at")
            .first()
        )

    answer_queryset = current_question.answers.all()
    next_question = (  # later created question
        Question.objects.filter(created_at__gt=current_question.created_at)
        .order_by("created_at")
        .first()
    )
    for _unused in range(1):  # for `break` functionality
        if request.method != "POST":
            form = SelectAnswerForm(answer_queryset=answer_queryset)
            break

        form = SelectAnswerForm(request.POST, answer_queryset=answer_queryset)
        if not form.is_valid():
            break

        # If a new answer "contradicts" previous, update it
        # Remove `ORDER BY` SQL because it's incompatible with unions in SQLite
        selected_before = answer_queryset.order_by().intersection(
            saved_progress.selected_answers.all().order_by()
        )
        if selected_before.exists():
            logger.debug("Removing previous contradicting answers: %s", selected_before)
            saved_progress.selected_answers.remove(*selected_before)
            pass

        saved_progress.selected_answers.add(form.cleaned_data["selected_answer"])

        if "submit-previous" in request.POST and previous_question is None:
            break  # just don't do anything
        if "submit-previous" in request.POST:
            saved_progress.question_in_progress = previous_question
            saved_progress.save()
            return redirect("htest-question", progress_id=saved_progress.id)

        if "submit-next" in request.POST and next_question is None:
            saved_progress.question_in_progress = None
            saved_progress.save()
            return redirect("htest-result", progress_id=saved_progress.id)
        if "submit-next" in request.POST:
            saved_progress.question_in_progress = next_question
            saved_progress.save()
            return redirect("htest-question", progress_id=saved_progress.id)
        # Do nothing if somehow neither button was pressed

    context = {
        "form": form,  # pyright: ignore[reportPossiblyUnboundVariable] # false positive?
        "question": current_question,
        "question_position": Question.objects.filter(
            created_at__lte=current_question.created_at  # lt -> 0..(n-1), lte -> 1..n
        ).count(),
        "total_questions": Question.objects.count(),
    }
    return render(request, "hyiptest/htest_question.html", context)


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
