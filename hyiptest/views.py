from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
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
    query = None
    search_executed = False
    found_badsite = None

    if "q" in request.GET:
        # Validate submitted form
        form = SearchDomainForm(request.GET)
        query = request.GET["q"]
        if form.is_valid():
            # Or if result is a separate page:
            # return redirect("search-domain-result", query=query)
            search_executed = True
            try:
                found_badsite = BadDomain.objects.get(name=query).site
            except BadDomain.DoesNotExist:
                pass
    else:
        # New form
        form = SearchDomainForm()

    context = {
        "form": form,
        "query": query,
        "search_executed": search_executed,
        "found_badsite": found_badsite,
    }
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

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception:
            return HttpResponseRedirect(
                reverse("question-delete", kwargs={"pk": self.object.pk})
            )


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
        saved_progress = HtestSnapshot.objects.get(  # TODO: implement handling wrong id
            id=progress_id
        )
        current_question = Question.objects.get(
            id=saved_progress.question_in_progress.id
        )

    if request.method == "POST":
        form = SelectAnswerForm(request.POST, question_obj=current_question)
        if form.is_valid():
            saved_progress.total_risk_score += form.cleaned_data[
                "selected_answer"
            ].risk_score

            # Find the questions after the current one, order them, get next
            next_question = (
                Question.objects.filter(created_at__gt=current_question.created_at)
                .order_by("created_at")
                .first()
            )
            saved_progress.question_in_progress = next_question
            saved_progress.save()
            if next_question is None:  # this was the last question
                return redirect("home")  # redirect to home page, for now
            return redirect(
                "htest-question", progress_id=saved_progress.id  # next question
            )
    else:
        form = SelectAnswerForm(question_obj=current_question)

    context = {
        "form": form,
        "question": current_question,
        "question_position": Question.objects.filter(
            created_at__lte=current_question.created_at  # lt -> 0..(n-1), lte -> 1..n
        ).count(),
        "total_questions": Question.objects.count(),
    }
    return render(request, "hyiptest/htest_question.html", context)
