from django.urls import include, path
from rest_framework import routers

from api import views

router = routers.DefaultRouter()
router.register(r"questions", views.QuestionViewSet, basename="question")

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
]
