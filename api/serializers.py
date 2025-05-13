from hyiptest.models import BadDomain, BadSite, Question
from rest_framework import serializers


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Question
        fields = ["url", "id", "text", "description", "created", "updated"]
        # The app namespace is not included by default.
        extra_kwargs = {"url": {"view_name": "api:question-detail"}}


class BadSiteSerializer(serializers.HyperlinkedModelSerializer):
    domains = serializers.HyperlinkedIdentityField(
        many=True,
        view_name="api:baddomain-detail",
        read_only=True,  # needed to hide field from the POST/PUT api form
    )

    class Meta:
        model = BadSite
        fields = ["url", "id", "name", "bad_type", "domains", "created", "updated"]
        extra_kwargs = {"url": {"view_name": "api:badsite-detail"}}


class BadDomainSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BadDomain
        fields = ["url", "id", "name", "site", "created", "updated"]
        extra_kwargs = {
            "url": {"view_name": "api:baddomain-detail"},
            "site": {"view_name": "api:badsite-detail"},
        }
