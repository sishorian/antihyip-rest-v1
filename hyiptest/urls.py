from django.urls import path

from hyiptest import views

urlpatterns = []

# Home page
urlpatterns += [
    path("", views.HomePageView.as_view(), name="home"),
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
    path("search-domain/", views.search_domain, name="search-domain"),
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
    path(
        "questions/create/",
        views.QuestionCreateView.as_view(),
        name="question-create",
    ),
    path(
        "questions/<uuid:pk>/update/",
        views.QuestionUpdateView.as_view(),
        name="question-update",
    ),
    path(
        "questions/<uuid:pk>/delete/",
        views.QuestionDeleteView.as_view(),
        name="question-delete",
    ),
]

# HtestSnapshot
urlpatterns += [
    path(
        "test/unfinished/",
        views.HtestSnapshotListView.as_view(),
        name="htestsnapshot-list",
    ),
    path(
        "test/unfinished/<uuid:pk>/",
        views.HtestSnapshotDetailView.as_view(),
        name="htestsnapshot-detail",
    ),
]

# The test
urlpatterns += [
    path("test/", views.htest_question, name="htest-question"),
    path("test/<uuid:progress_id>/", views.htest_question, name="htest-question"),
]
