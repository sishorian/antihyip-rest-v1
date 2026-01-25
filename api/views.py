from django.contrib.auth import get_user_model
from hyiptest.models import BadSite, HtestProgress, Question
from rest_framework import permissions, viewsets

from api.serializers import (
    BadSiteSerializer,
    HtestProgressSerializer,
    QuestionSerializer,
    UserSerializer,
)


class BadSiteViewSet(viewsets.ModelViewSet):
    serializer_class = BadSiteSerializer
    queryset = BadSite.objects.all()


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # User list must be private
    queryset = get_user_model().objects.all()


class HtestProgressViewSet(viewsets.ModelViewSet):
    serializer_class = HtestProgressSerializer
    # If omitted, causes an exception for AnonymousUser
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Except for staff, limit view access to only user's own instances.
        """
        if self.request.user.is_staff:
            return HtestProgress.objects.all()
        return HtestProgress.objects.filter(user=self.request.user)
