import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import BadRequest
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from hyiptest.forms import SearchDomainForm, SelectAnswerForm
from hyiptest.models import BadDomain, BadSite, HtestProgress, Question


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


class QuestionCreateView(PermissionRequiredMixin, generic.CreateView):
    model = Question
    fields = ["text", "description"]
    permission_required = "hyiptest.add_question"


class QuestionUpdateView(PermissionRequiredMixin, generic.UpdateView):
    model = Question
    fields = ["text", "description"]
    permission_required = "hyiptest.change_question"


class QuestionDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = Question
    success_url = reverse_lazy("question-list")
    permission_required = "hyiptest.delete_question"


# HtestProgress


class HtestProgressListView(LoginRequiredMixin, generic.ListView):
    """
    View displaying completed and incomplete tests started by a user.
    """

    model = HtestProgress
    paginate_by = 20

    def get_queryset(self):
        return HtestProgress.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


class HtestProgressDetailView(LoginRequiredMixin, generic.DetailView):
    model = HtestProgress

    def get_queryset(self):
        """
        Only lookup among user's progresses.

        Search by pk will be performed on this queryset, 404 if missing.
        """
        return HtestProgress.objects.filter(user=self.request.user)


# HyipTest (Htest)
# Just `test_` can be confused with unittest


@login_required
def htest_start(request):
    """
    View to create new HtestProgress for HtestQuestionView, then redirect to it.
    """
    first_question = Question.objects.earliest("created_at")
    progress = HtestProgress.objects.create(
        question_in_progress=first_question, user=request.user
    )
    logger.debug("Created HtestProgress instance: %s", progress)

    return redirect("htest-question", progress_id=progress.id)


class HtestQuestionView(LoginRequiredMixin, generic.TemplateView):
    """
    View for asking user one question from the test.

    Inheriting from generic.TemplateView
    because using generic.FormView was too confusing.
    """

    template_name = "hyiptest/htest_question.html"

    def get_test_progress(self, progress_id):
        """
        Return HtestProgress instance of the test.
        """
        progress = get_object_or_404(HtestProgress, id=progress_id)

        if progress.user != self.request.user:
            raise Http404("Attempt to continue someone else's test")
        if progress.question_in_progress is None:
            raise BadRequest("Attempt to resume a test that is already finised")

        return progress

    def get_test_form_initial(self, progress):
        question_answers = progress.question_in_progress.answers.all()
        progress_answers = progress.selected_answers.all()
        initially_selected = (
            # Remove `ORDER BY` SQL because it's incompatible with unions in SQLite
            question_answers.order_by()
            .intersection(progress_answers.order_by())
            .first()
        )
        return initially_selected

    def get_test_form(self, progress, form_data=None):
        """
        Create form for the test question.
        """
        question_answers = progress.question_in_progress.answers.all()
        initially_selected = self.get_test_form_initial(progress)

        if initially_selected is None:
            return SelectAnswerForm(data=form_data, answer_queryset=question_answers)
        return SelectAnswerForm(
            data=form_data,
            initial={"selected_answer": initially_selected},
            answer_queryset=question_answers,
        )

    def get_context_data(self, progress, form, **kwargs):
        context = super().get_context_data(**kwargs)
        current_question = progress.question_in_progress

        context["form"] = form
        context["current_question"] = current_question
        context["current_question_position"] = Question.objects.filter(
            # questions created before current, lt -> 0..(n-1), lte -> 1..n
            created_at__lte=current_question.created_at
        ).count()
        context["total_questions"] = Question.objects.count()

        # These will be None on the first and the last question
        context["previous_question"] = Question.objects.filter(
            created_at__lt=current_question.created_at  # previously created questions
        ).last()  # automatically ordered by Meta.ordering
        context["next_question"] = Question.objects.filter(
            created_at__gt=current_question.created_at  # later created questions
        ).first()

        return context

    def get(self, request, *args, **kwargs):
        progress = self.get_test_progress(kwargs["progress_id"])
        context = self.get_context_data(
            progress, self.get_test_form(progress), **kwargs
        )
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        progress = self.get_test_progress(kwargs["progress_id"])
        form = self.get_test_form(progress, request.POST)
        context = self.get_context_data(progress, form, **kwargs)

        if not form.is_valid():
            logger.debug("Invalid form data: %s", request.POST)
            return self.render_to_response(context)

        initially_selected = self.get_test_form_initial(progress)
        # If a new answer "contradicts" previous, change it
        if initially_selected is not None:
            logger.debug(
                "Removing previously selected answer: %s", repr(initially_selected)
            )
            progress.selected_answers.remove(initially_selected)
        progress.selected_answers.add(form.cleaned_data["selected_answer"])

        previous_question = context["previous_question"]
        if "submit-previous" in request.POST and previous_question is None:
            raise BadRequest("Attempt to go to question previous to the first")
        if "submit-previous" in request.POST:
            progress.question_in_progress = previous_question
            progress.save()
            return redirect("htest-question", progress_id=progress.id)
        next_question = context["next_question"]
        if "submit-next" in request.POST and next_question is None:
            progress.question_in_progress = None
            progress.save()
            return redirect("htest-result", progress_id=progress.id)
        if "submit-next" in request.POST:
            progress.question_in_progress = next_question
            progress.save()
            return redirect("htest-question", progress_id=progress.id)

        raise BadRequest("Form submitted but neither action was triggered")


class HtestResultView(LoginRequiredMixin, generic.TemplateView):
    template_name = "hyiptest/htest_result.html"

    def get_context_data(self, **kwargs):
        def result_is_bad(result):
            return result >= 100

        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        progress = get_object_or_404(HtestProgress, id=kwargs["progress_id"])
        if progress.user != self.request.user:
            raise Http404("Attempt to view result of someone else's test")
        if progress.question_in_progress is not None:
            raise BadRequest("Attempt to view result of unfinished test")

        context["result_is_bad"] = result_is_bad(progress.get_total_risk_score())
        return context
