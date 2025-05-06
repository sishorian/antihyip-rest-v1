from django.urls import include, path
from rest_framework import routers

from hyiptest import views

router = routers.DefaultRouter()
router.register(r"questions", views.QuestionViewSet, basename="question")

urlpatterns = [
    path("", include(router.urls)),
]
