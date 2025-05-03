from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from hyiptest import views

urlpatterns = []

# Question
urlpatterns += [
    path("questions/", views.QuestionList.as_view(), name="question-list"),
]

# Add urls with .format.
urlpatterns = format_suffix_patterns(urlpatterns)
