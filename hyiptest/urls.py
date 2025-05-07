from django.urls import path

from hyiptest import views

urlpatterns = [
    # Question
    path("questions/", views.QuestionListView.as_view(), name="question-list"),
    path(
        "questions/<uuid:pk>/",
        views.QuestionDetailView.as_view(),
        name="question-detail",
    ),
]
