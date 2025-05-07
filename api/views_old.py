from django.shortcuts import get_object_or_404

from hyiptest.models import Question
from rest_framework import generics, mixins, renderers, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import QuestionSerializer


class QuestionList1(APIView):
    """
    Old view. List all questions, with template support.

    Can either return objects in API formats or in a regular template.
    """

    renderer_classes = [
        renderers.TemplateHTMLRenderer,
        renderers.JSONRenderer,
        renderers.BrowsableAPIRenderer,
    ]

    def get(self, request, format=None):
        queryset = Question.objects.all()
        # TemplateHTMLRenderer takes a context dict, not requiring serialization.
        if request.accepted_renderer.format == "html":
            data = {"question_list": queryset}
            return Response(data, template_name="hyiptest/question_list.html")
        serializer = QuestionSerializer(queryset, many=True)
        return Response(serializer.data)


class QuestionList2(mixins.ListModelMixin, generics.GenericAPIView):
    """
    Old view. List all questions, with template support.

    Can either return objects in API formats or in a regular template.
    """

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    renderer_classes = [
        renderers.TemplateHTMLRenderer,
        renderers.JSONRenderer,
        renderers.BrowsableAPIRenderer,
    ]

    def get(self, request, *args, **kwargs):
        if request.accepted_renderer.format == "html":
            # Get queryset with applied filtering; from self.list() code.
            queryset = self.filter_queryset(self.get_queryset())
            data = {"question_list": queryset}
            return Response(data, template_name="hyiptest/question_list.html")
        return self.list(request, *args, **kwargs)


class QuestionViewSet3(viewsets.ViewSet):
    """
    Old viewset. List all questions or retrieve one, with template support.

    Can either return objects in API formats or in a regular template.
    """

    renderer_classes = [
        renderers.TemplateHTMLRenderer,
        renderers.JSONRenderer,
        renderers.BrowsableAPIRenderer,
    ]

    def list(self, request, format=None):
        queryset = Question.objects.all()
        if request.accepted_renderer.format == "html":
            data = {"question_list": queryset}
            return Response(data, template_name="hyiptest/question_list.html")
        serializer = QuestionSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, format=None):
        queryset = Question.objects.all()
        question = get_object_or_404(queryset, pk=pk)
        if request.accepted_renderer.format == "html":
            data = {"question": question}
            return Response(data, template_name="hyiptest/question_detail.html")
        serializer = QuestionSerializer(question)
        return Response(serializer.data)
