from hyiptest.models import Question
from rest_framework import serializers


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Question
        fields = ["url", "id", "text", "description", "updated", "created"]
        # The app namespace is not included by default.
        extra_kwargs = {"url": {"view_name": "api:question-detail"}}
