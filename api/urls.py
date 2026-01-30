from django.urls import include, path
from rest_framework import routers

from api import views

router = routers.DefaultRouter()
router.register("badsites", views.BadSiteViewSet, basename="badsite")
router.register("questions", views.QuestionViewSet, basename="question")
router.register("users", views.UserViewSet, basename="user")
router.register("test-progresses", views.HtestProgressViewSet, basename="htestprogress")

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
    path("start-test/", views.HtestStart.as_view(), name="htest-start"),
]
