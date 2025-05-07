from rest_framework import serializers

from hyiptest.models import Question


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Question
        fields = ["url", "id", "text", "description", "updated", "created"]
