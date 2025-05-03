from rest_framework.renderers import (
    BrowsableAPIRenderer,
    JSONRenderer,
    TemplateHTMLRenderer,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from hyiptest.models import Question
from hyiptest.serializers import QuestionSerializer


class QuestionList(APIView):
    """
    List all questions.
    """

    renderer_classes = [TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer]

    def get(self, request, format=None):
        questions = Question.objects.all()
        if request.accepted_renderer.format == "html":
            # TemplateHTMLRenderer takes a context dict, not requiring serialization.
            data = {"question_list": questions}
            return Response(data, template_name="hyiptest/question_list.html")
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
