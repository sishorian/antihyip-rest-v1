from django.urls import include, path
from rest_framework import routers

from api import views

router = routers.DefaultRouter()
router.register(r"questions", views.QuestionViewSet, basename="question")
router.register(r"badsites", views.BadSiteViewSet, basename="badsite")
router.register(r"baddomains", views.BadDomainViewSet, basename="baddomain")

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
]
