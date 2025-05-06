from rest_framework import viewsets

from hyiptest.models import Question
from hyiptest.serializers import QuestionSerializer


'''
# Old view that allowed to also render html templates.
class QuestionList(mixins.ListModelMixin, generics.GenericAPIView):
    """
    List all questions.
    """

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    renderer_classes = [
        renderers.TemplateHTMLRenderer,
        renderers.JSONRenderer,
        renderers.BrowsableAPIRenderer,
    ]

    def get(self, request, *args, **kwargs):
        # TemplateHTMLRenderer takes a context dict, not requiring serialization.
        if request.accepted_renderer.format == "html":
            # Get queryset with applied filtering; from self.list() code.
            queryset = self.filter_queryset(self.get_queryset())
            data = {"question_list": queryset}
            return Response(data, template_name="hyiptest/question_list.html")
        return self.list(request, *args, **kwargs)
'''


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
