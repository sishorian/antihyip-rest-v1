import uuid

from django.conf import settings
from django.contrib import admin
from django.core.validators import DomainNameValidator
from django.db import models
from django.db.models import Q, Sum
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

    created_at = models.DateTimeField(auto_now_add=True, help_text=_("Creation time"))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("Modification time"))

    def __str__(self):
        return str(self.id)

    class Meta:
        abstract = True
        ordering = ["created_at"]  # will suffice initially for most models


class BadSite(UUIDTimestampsModel):
    """
    Model representing a website known to be a fraud.
    """

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Name of the site or its company behind it"),
    )

    # Can be the exactly same, but shouldn't be "similarly same": "Fraud" and "fraud".
    # Difficult to enforce.
    bad_type = models.CharField(
        max_length=50,
        unique=False,
        help_text=_("What type of fraud it is, e.g. pyramid, scam, etc."),
    )

    def display_domains(self):
        """
        Create a short string of the first domain plus number of remaining.
        """
        num_domains = self.domains.count()
        first_domain = self.domains.first()
        match num_domains:
            case 0:
                return "-"
            case 1:
                return f"{first_domain}"
        return f"{first_domain}, ...+{num_domains - 1}"

    display_domains.short_description = "Domains"

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("badsite-detail", kwargs={"pk": self.pk})

    class Meta(UUIDTimestampsModel.Meta):
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="badsite_name_lower_unique",
                violation_error_message=_("BadSite already exists (lowercase match)"),
            ),
        ]


class BadDomain(UUIDTimestampsModel):
    """
    Model representing one of the domains of a BadSite instance.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[DomainNameValidator(message=_("Enter a valid domain name"))],
        help_text=_("Domain name of the BadSite"),
    )

    site = models.ForeignKey(
        BadSite,
        on_delete=models.CASCADE,
        related_name="domains",
        help_text=_("Name of the site this domain belongs to"),
    )

    def __str__(self):
        return str(self.name)

    def clean(self):
        """
        Make sure domain names are lowercase.
        """
        self.name = self.name.lower()

    class Meta(UUIDTimestampsModel.Meta):
        constraints = [
            # Check if it's lowercase in cases where clean() is not run.
            # The UniqueConstraint is not needed.
            models.CheckConstraint(
                condition=Q(name=Lower("name")),
                name="baddomain_name_is_lower",
            ),
        ]


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

    def __str__(self):
        return str(self.text)

    def get_absolute_url(self):
        return reverse("question-detail", kwargs={"pk": self.pk})

    # TODO: Custom ordering
    class Meta(UUIDTimestampsModel.Meta):  # Django will set abstract=False.
        constraints = [
            models.UniqueConstraint(
                Lower("text"),
                name="question_text_lower_unique",
                violation_error_message=_("Question already exists (lowercase match)"),
            ),
        ]


class Answer(UUIDTimestampsModel):
    """
    Model representing an answer to a specific question.
    """

    # TODO: Meta.order_with_respect_to
    text = models.CharField(max_length=100, help_text=_("The answer itself"))
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("What it means, in more words"),
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        help_text=_("The question it belongs to"),
    )
    risk_score = models.PositiveSmallIntegerField(
        help_text=_("Bad points for a site"),
    )

    def __str__(self):
        return str(self.text)


# htest - short for hyiptest
# Just `test` can be confused with unittest.
class HtestProgress(UUIDTimestampsModel):
    """
    Model representing a test instance started by user.

    Can represent both completed and incomplete tests.
    If test is completed, question_in_progress is null.
    """

    question_in_progress = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_(
            "Question currently displayed to the user, null if test is completed"
        ),
    )
    selected_answers = models.ManyToManyField(
        Answer, help_text=_("Answers the user has selected")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text=_("User that started the test"),
    )

    @property
    @admin.display(description=_("Total Risk Score"))
    def total_risk_score(self):
        aggregate_dict = self.selected_answers.aggregate(Sum("risk_score"))
        return aggregate_dict["risk_score__sum"]

    def get_absolute_url(self):
        return reverse("htestprogress-detail", kwargs={"pk": self.pk})

    class Meta(UUIDTimestampsModel.Meta):
        ordering = ["-updated_at"]
