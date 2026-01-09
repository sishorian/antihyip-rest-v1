import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest, SuspiciousOperation
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic

from hyiptest.forms import SelectAnswerForm
from hyiptest.models import HtestProgress, Question


logger = logging.getLogger(__name__)


def htest_question(request, progress_id=None):
    """
    View function for asking user one question from the test.
    """

    if progress_id is None:  # user takes new test
        current_question = Question.objects.order_by("created_at").first()
        previous_question = None  # shouldn't be any questions created before the first
        # Delete all previous incomplete tests, for now
        HtestProgress.objects.filter(question_in_progress__isnull=False).delete()
        # New save
        saved_progress = HtestProgress.objects.create(
            question_in_progress=current_question
        )
    else:
        saved_progress = get_object_or_404(HtestProgress, id=progress_id)
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


# Overriding setup() is actually a bad idea
class HtestQuestionView(generic.View):
    """
    View for asking user one question from the test.
    """

    def setup(self, request, *args, **kwargs):
        if kwargs["progress_id"] is None:  # new test created
            # Delete all previous incomplete tests, for now
            HtestProgress.objects.filter(question_in_progress__isnull=False).delete()

            kwargs["current_question"] = Question.objects.order_by("created_at").first()
            kwargs["saved_progress"] = HtestProgress.objects.create(
                question_in_progress=kwargs["current_question"]
            )
        else:  # test in progress or resumed
            kwargs["saved_progress"] = get_object_or_404(
                HtestProgress, id=kwargs["progress_id"]
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


# Doesn't work with LoginRequiredMixin, probably because of overriding setup()
class HtestQuestionView1(LoginRequiredMixin, generic.FormView):
    """
    View for asking user one question from the test.
    """

    template_name = "hyiptest/htest_question.html"
    form_class = SelectAnswerForm

    def setup(self, request, *args, **kwargs):
        """Insert data in self.kwargs for the other methods."""
        super().setup(request, *args, **kwargs)  # kwargs -> self.kwargs

        progress_id = self.kwargs["progress_id"]
        # New test created
        if progress_id is None:
            current_question = Question.objects.earliest("created_at")
            saved_progress = HtestProgress.objects.create(
                question_in_progress=current_question, user=request.user
            )
        # Test in progress or resumed
        else:
            saved_progress = get_object_or_404(HtestProgress, id=progress_id)
            if saved_progress.user != request.user:
                raise SuspiciousOperation("Attempt to continue someone else's test")
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

        logger.debug("self.request.POST = %s", self.request.POST)  # for writing tests

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
        kwargs["current_question_position"] = Question.objects.filter(
            # lt -> 0..(n-1), lte -> 1..n
            created_at__lte=current_question.created_at
        ).count()
        kwargs["total_questions"] = Question.objects.count()
        kwargs["current_question"] = current_question
        kwargs["previous_question"] = self.kwargs["previous_question"]
        kwargs["next_question"] = self.kwargs["next_question"]

        return super().get_context_data(**kwargs)


# get_test_progress is called twice: first by get(), then post().
class HtestQuestionView2(LoginRequiredMixin, generic.TemplateView):
    """
    View for asking user one question from the test.

    Inheriting from generic.TemplateView
    because using generic.FormView was too confusing.
    """

    template_name = "hyiptest/htest_question.html"

    def get_test_progress(self, progress_id):
        """
        Return HtestProgress instance of the test.

        Must be called only once.
        """

        # New test requested
        if progress_id is None:
            first_question = Question.objects.earliest("created_at")
            progress = HtestProgress.objects.create(
                question_in_progress=first_question, user=self.request.user
            )

            logger.debug("Created HtestProgress instance: %s", progress)
            return progress

        # Continuing previously created test
        progress = get_object_or_404(HtestProgress, id=progress_id)
        if progress.user != self.request.user:
            raise SuspiciousOperation("Attempt to continue someone else's test")
        if progress.question_in_progress is None:
            raise BadRequest("Attempt to resume a test that is already finised")

        return progress

    def get_test_form(self, test_progress, form_data=None):
        """
        Create form for the test question.
        """

        displayed_answers = test_progress.question_in_progress.answers.all()
        selected_before = (
            # Remove `ORDER BY` SQL because it's incompatible with unions in SQLite
            displayed_answers.order_by()
            .intersection(test_progress.selected_answers.all().order_by())
            .first()
        )

        if selected_before is None:
            return SelectAnswerForm(data=form_data, answer_queryset=displayed_answers)
        return SelectAnswerForm(
            data=form_data,
            initial={"selected_answer": selected_before},
            answer_queryset=displayed_answers,
        )

    def get_context_data(self, progress, form, **kwargs):
        context = super().get_context_data(**kwargs)  # handles self.extra_context

        current_question = progress.question_in_progress
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

        context["form"] = form
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
            return self.render_to_response(context)

        displayed_answers = progress.question_in_progress.answers.all()
        selected_before = (
            # Remove `ORDER BY` SQL because it's incompatible with unions in SQLite
            displayed_answers.order_by()
            .intersection(progress.selected_answers.all().order_by())
            .first()
        )
        # If a new answer "contradicts" previous, change it
        if selected_before is not None:
            logger.debug(
                "Removing previous contradicting answer: %s", repr(selected_before)
            )
            progress.selected_answers.remove(selected_before)
        # From the docs, this shouldn't add duplicates
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
