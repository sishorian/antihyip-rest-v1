import uuid

from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _


class Question(models.Model):
    """
    Model representing a single question for the user.
    """

    id = models.UUIDField(
        "ID",
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier"),
    )

    text = models.CharField(
        max_length=100, unique=True, help_text=_("The question itself")
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Explain the question to the user"),
    )

    updated = models.DateTimeField(auto_now=True, help_text=_("Modification time"))
    created = models.DateTimeField(auto_now_add=True, help_text=_("Creation time"))

    class Meta:
        ordering = ["created"]  # This ordering will work for now.
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
