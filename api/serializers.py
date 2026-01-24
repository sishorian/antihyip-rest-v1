from django.contrib.auth import get_user_model
from hyiptest.models import Answer, BadSite, HtestProgress, Question
from rest_framework import serializers


class BadSiteSerializer(serializers.HyperlinkedModelSerializer):
    domains = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )

    class Meta:
        model = BadSite
        fields = [
            "url",
            "name",
            "bad_type",
            "domains",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {"url": {"view_name": "api:badsite-detail"}}


class AnswerSerializer(serializers.ModelSerializer):
    # Needed for HtestProgress views
    question = serializers.HyperlinkedRelatedField(
        read_only=True, view_name="api:question-detail"
    )

    class Meta:
        model = Answer
        fields = [
            "id",
            "text",
            "description",
            "question",
            "risk_score",
            "created_at",
            "updated_at",
        ]


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["url", "text", "description", "answers", "created_at", "updated_at"]
        extra_kwargs = {"url": {"view_name": "api:question-detail"}}


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["url", "username", "email"]
        extra_kwargs = {"url": {"view_name": "api:user-detail"}}


class HtestProgressSerializer(serializers.HyperlinkedModelSerializer):
    selected_answers = AnswerSerializer(many=True, required=False)

    class Meta:
        model = HtestProgress
        fields = [
            "url",
            "user",
            "question_in_progress",
            "selected_answers",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "url": {"view_name": "api:htestprogress-detail"},
            "user": {"read_only": True, "view_name": "api:user-detail"},
            "question_in_progress": {"view_name": "api:question-detail"},
        }

    def create(self, validated_data):
        # Need to be set after instance creation
        selected_answers = validated_data.pop("selected_answers", None)

        instance = HtestProgress.objects.create(**validated_data)
        if selected_answers:
            instance.selected_answers.set(selected_answers)

    def update(self, instance, validated_data):
        instance.question_in_progress = validated_data.get(
            "question_in_progress", instance.question_in_progress
        )
        instance.save()

        selected_answers = validated_data.get("selected_answers", None)
        if selected_answers:
            instance.selected_answers.set(selected_answers)
