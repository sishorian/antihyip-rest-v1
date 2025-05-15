from django.urls import path

from hyiptest import views

urlpatterns = []

# Home page
urlpatterns += [
    path("", views.HomePageView.as_view(), name="home"),
]

# Question
urlpatterns += [
    path("questions/", views.QuestionListView.as_view(), name="question-list"),
    path(
        "questions/<uuid:pk>/",
        views.QuestionDetailView.as_view(),
        name="question-detail",
    ),
    path(
        "questions/create/", views.QuestionCreateView.as_view(), name="question-create"
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

# BadSite
urlpatterns += [
    path("badsites/", views.BadSiteListView.as_view(), name="badsite-list"),
    path(
        "badsites/<uuid:pk>/",
        views.BadSiteDetailView.as_view(),
        name="badsite-detail",
    ),
]
