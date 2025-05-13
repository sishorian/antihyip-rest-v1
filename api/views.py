from hyiptest.models import BadDomain, BadSite, Question
from rest_framework import viewsets

from api.serializers import BadDomainSerializer, BadSiteSerializer, QuestionSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class BadSiteViewSet(viewsets.ModelViewSet):
    queryset = BadSite.objects.all()
    serializer_class = BadSiteSerializer


class BadDomainViewSet(viewsets.ModelViewSet):
    queryset = BadDomain.objects.all()
    serializer_class = BadDomainSerializer
