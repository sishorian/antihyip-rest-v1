from rest_framework import serializers

from hyiptest.models import Question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "text", "description", "updated", "created"]
