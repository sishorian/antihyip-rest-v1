from rest_framework import viewsets

from hyiptest.models import Question
from hyiptest.serializers import QuestionSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
