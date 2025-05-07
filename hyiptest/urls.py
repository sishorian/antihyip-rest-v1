from django.urls import path

from hyiptest import views

urlpatterns = []

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
