import logging

from django.core.exceptions import BadRequest
from django.shortcuts import get_object_or_404, redirect
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


class HtestQuestionView(generic.FormView):
    """
    View for asking user one question from the test.
    """

    template_name = "hyiptest/htest_question.html"
    form_class = SelectAnswerForm

    def setup(self, request, *args, **kwargs):
        """Insert data in self.kwargs for the other methods."""
        super().setup(request, *args, **kwargs)  # kwargs -> self.kwargs

        progress_id = self.kwargs["progress_id"]
        if progress_id is None:  # new test created
            current_question = Question.objects.earliest("created_at")
            saved_progress = HtestSnapshot.objects.create(
                question_in_progress=current_question
            )
        else:  # test in progress or resumed
            saved_progress = get_object_or_404(HtestSnapshot, id=progress_id)
            current_question = saved_progress.question_in_progress
            if current_question is None:
                raise BadRequest("Attempt to resume a test that is already finised")
        # Answers belonging to current_question
        displayed_answers = current_question.answers.all()

        # Previously created question, should be None on the first question
        self.kwargs["previous_question"] = Question.objects.filter(
            created_at__lt=current_question.created_at
        ).last()  # automatically ordered by Meta.ordering
        # Later created question
        self.kwargs["next_question"] = Question.objects.filter(
            created_at__gt=current_question.created_at
        ).first()
        # Displayed answer that was already selected in saved_progress
        self.kwargs["selected_before"] = (
            # Remove `ORDER BY` SQL because it's incompatible with unions in SQLite
            displayed_answers.order_by()
            .intersection(saved_progress.selected_answers.all().order_by())
            .first()
        )
        #
        self.kwargs["current_question"] = current_question
        self.kwargs["saved_progress"] = saved_progress
        self.kwargs["displayed_answers"] = displayed_answers

    def get_initial(self):
        """Return the initial data for the form."""
        selected_before = self.kwargs["selected_before"]
        if selected_before is None:
            return {}
        return {"selected_answer": selected_before}

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        kwargs.update({"answer_queryset": self.kwargs["displayed_answers"]})
        return kwargs

    def form_valid(self, form):
        """Actions performed if the submitted form is valid."""
        saved_progress = self.kwargs["saved_progress"]

        # If a new answer "contradicts" previous, change it
        selected_before = self.kwargs["selected_before"]
        if selected_before is not None:
            logger.debug(
                "Removing previous contradicting answer: %s", repr(selected_before)
            )
            saved_progress.selected_answers.remove(selected_before)

        # From the docs, this won't add duplicates
        saved_progress.selected_answers.add(form.cleaned_data["selected_answer"])

        previous_question = self.kwargs["previous_question"]
        if "submit-previous" in self.request.POST and previous_question is None:
            # Just refresh form, for now
            # From super().form_invalid() code
            return self.render_to_response(self.get_context_data(form=form))
        if "submit-previous" in self.request.POST:
            saved_progress.question_in_progress = previous_question
            saved_progress.save()
            return redirect("htest-question", progress_id=saved_progress.id)

        next_question = self.kwargs["next_question"]
        if "submit-next" in self.request.POST and next_question is None:
            saved_progress.question_in_progress = None
            saved_progress.save()
            return redirect("htest-result", progress_id=saved_progress.id)
        if "submit-next" in self.request.POST:
            saved_progress.question_in_progress = next_question
            saved_progress.save()
            return redirect("htest-question", progress_id=saved_progress.id)

        raise BadRequest("Form submitted but neither action was triggered")

    def get_context_data(self, **kwargs):
        """Insert data into the template context."""
        current_question = self.kwargs["current_question"]
        kwargs["current_question"] = current_question
        kwargs["current_question_position"] = Question.objects.filter(
            # lt -> 0..(n-1), lte -> 1..n
            created_at__lte=current_question.created_at
        ).count()
        kwargs["total_questions"] = Question.objects.count()

        return super().get_context_data(**kwargs)


class HtestResultView(generic.TemplateView):
    template_name = "hyiptest/htest_result.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        def result_is_bad(result):
            return result >= 100

        context["result_is_bad"] = result_is_bad(
            get_object_or_404(
                HtestSnapshot, id=kwargs["progress_id"]
            ).get_total_risk_score()
        )
        return context
