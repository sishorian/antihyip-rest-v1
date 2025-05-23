from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic

from hyiptest.forms import DomainSearchForm
from hyiptest.models import BadSite, Question


class HomePageView(generic.TemplateView):
    template_name = "home.html"


class DomainSearchView(generic.FormView):
    template_name = "hyiptest/domainsearch_form.html"
    form_class = DomainSearchForm
    success_url = reverse_lazy("home")  # for now


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


# BadSite


class BadSiteListView(generic.ListView):
    model = BadSite
    paginate_by = 20


class BadSiteDetailView(generic.DetailView):
    model = BadSite
