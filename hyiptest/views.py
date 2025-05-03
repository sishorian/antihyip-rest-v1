from rest_framework.response import Response
from rest_framework.views import APIView

from hyiptest.models import Question
from hyiptest.serializers import QuestionSerializer


class QuestionList(APIView):
    """
    List all questions.
    """

    def get(self, request, format=None):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
