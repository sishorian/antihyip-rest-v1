from django.contrib.auth import get_user_model
from hyiptest.models import BadSite, HtestProgress, Question
from rest_framework import viewsets

from api.serializers import (
    BadSiteSerializer,
    HtestProgressSerializer,
    QuestionSerializer,
    UserSerializer,
)


class BadSiteViewSet(viewsets.ModelViewSet):
    queryset = BadSite.objects.all()
    serializer_class = BadSiteSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class HtestProgressViewSet(viewsets.ModelViewSet):
    # Filter by user?
    queryset = HtestProgress.objects.all()
    serializer_class = HtestProgressSerializer
