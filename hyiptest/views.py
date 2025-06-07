from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import generic

from hyiptest.forms import SearchDomainForm
from hyiptest.models import BadDomain, BadSite, Question


class HomePageView(generic.TemplateView):
    template_name = "home.html"


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


# BadSite


class BadSiteListView(generic.ListView):
    model = BadSite
    paginate_by = 20


class BadSiteDetailView(generic.DetailView):
    model = BadSite
