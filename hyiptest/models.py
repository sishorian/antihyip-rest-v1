import uuid

from django.db import models
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class UUIDTimestampsModel(models.Model):
    """
    Base abstract model that has one UUIDField and two auto `DateTimeField`s.

    UUIDField `id` field is primary_key
    and 2 `DateTimeField`s are for creation and modification time.
    """

    id = models.UUIDField(
        "ID",
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier"),
    )

    created = models.DateTimeField(auto_now_add=True, help_text=_("Creation time"))
    updated = models.DateTimeField(auto_now=True, help_text=_("Modification time"))

    class Meta:
        abstract = True
        ordering = ["created"]  # will suffice initially for most models

    def __str__(self):
        return str(self.id)


class Question(UUIDTimestampsModel):
    """
    Model representing a single question for the user.
    """

    text = models.CharField(
        max_length=100, unique=True, help_text=_("The question itself")
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Explain the question to the user"),
    )

    class Meta(UUIDTimestampsModel.Meta):  # Django will set abstract=False.
        constraints = [
            models.UniqueConstraint(
                Lower("text"),
                name="question_text_unique_ci",  # 'ci' - case-insensitive
                violation_error_message=_(
                    "Same question text already exists (case-insensitive match)"
                ),
            ),
        ]

    def __str__(self):
        return str(self.text)

    def get_absolute_url(self):
        return reverse("question-detail", kwargs={"pk": self.pk})
