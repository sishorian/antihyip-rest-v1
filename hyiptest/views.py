from django.core.exceptions import BadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic

from hyiptest.forms import SearchDomainForm, SelectAnswerForm
from hyiptest.models import BadDomain, BadSite, HtestSnapshot, Question


class HomePageView(generic.TemplateView):
    template_name = "home.html"


# BadSite


class BadSiteListView(generic.ListView):
    model = BadSite
    paginate_by = 20


class BadSiteDetailView(generic.DetailView):
    model = BadSite


def search_domain(request):
    """
    View function for searching domain in the fraud database.
    """
    context = {
        "form": None,  # must be assigned later
        "query": None,
        "search_executed": False,
        "found_badsite": None,
    }

    if "q" in request.GET:  # submitted form
        context["form"] = SearchDomainForm(request.GET)
        context["query"] = request.GET["q"]
        if context["form"].is_valid():
            context["search_executed"] = True
            try:
                context["found_badsite"] = BadDomain.objects.get(
                    name=context["query"]
                ).site
            except BadDomain.DoesNotExist:
                context["found_badsite"] = None  # equivalent to just `pass`
    else:  # new form
        context["form"] = SearchDomainForm()

    return render(request, "hyiptest/search_domain.html", context)


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
        current_question = (
            Question.objects.order_by().first()  # start with the first created question
        )
        HtestSnapshot.objects.filter(
            question_in_progress__isnull=False
        ).delete()  # delete all previous incomplete tests, for now
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

    if request.method == "POST":
        form = SelectAnswerForm(
            request.POST, answer_queryset=current_question.answers.all()
        )
        if form.is_valid():
            saved_progress.selected_answers.add(form.cleaned_data["selected_answer"])

            # Find the questions after the current one, order them, get next
            next_question = (
                Question.objects.filter(created_at__gt=current_question.created_at)
                .order_by("created_at")
                .first()
            )
            saved_progress.question_in_progress = next_question
            saved_progress.save()
            # Finish the test (this was the last question)
            if next_question is None:
                return redirect("htest-result", progress_id=saved_progress.id)
            # Next question
            return redirect("htest-question", progress_id=saved_progress.id)
    else:
        form = SelectAnswerForm(answer_queryset=current_question.answers.all())

    context = {
        "form": form,
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
