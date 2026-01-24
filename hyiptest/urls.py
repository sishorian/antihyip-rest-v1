from django.urls import include, path

from hyiptest import views

urlpatterns = []

# Home page
urlpatterns += [
    path("", views.HomePageView.as_view(), name="home"),
]

# Django authentication urls (for login, logout, password management)
urlpatterns += [
    path("accounts/", include("django.contrib.auth.urls")),
]

# BadSite
urlpatterns += [
    path(
        "badsites/",
        views.BadSiteListView.as_view(),
        name="badsite-list",
    ),
    path(
        "badsites/<uuid:pk>/",
        views.BadSiteDetailView.as_view(),
        name="badsite-detail",
    ),
]

# Check website domain
urlpatterns += [
    path("search-domain/", views.SearchDomainView.as_view(), name="search-domain"),
]

# Question
urlpatterns += [
    path(
        "questions/",
        views.QuestionListView.as_view(),
        name="question-list",
    ),
    path(
        "questions/<uuid:pk>/",
        views.QuestionDetailView.as_view(),
        name="question-detail",
    ),
]

# HtestProgress
urlpatterns += [
    path(
        "previous-tests/",
        views.HtestProgressListView.as_view(),
        name="htestprogress-list",
    ),
    path(
        "previous-tests/<uuid:pk>/",
        views.HtestProgressDetailView.as_view(),
        name="htestprogress-detail",
    ),
    path(
        "previous-tests/<uuid:pk>/delete/",
        views.HtestProgressDeleteView.as_view(),
        name="htestprogress-delete",
    ),
]

# The test
urlpatterns += [
    path(
        "test/",
        views.htest_start,
        name="htest-start",
    ),
    path(
        "test/<uuid:progress_pk>/",
        views.HtestQuestionView.as_view(),
        name="htest-question",
    ),
    path(
        "test/<uuid:progress_pk>/result/",
        views.HtestResultView.as_view(),
        name="htest-result",
    ),
]
