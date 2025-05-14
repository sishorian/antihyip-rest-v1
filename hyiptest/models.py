import uuid

from django.core.validators import DomainNameValidator
from django.db import models
from django.db.models import Q
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

    def __str__(self):
        return str(self.id)

    class Meta:
        abstract = True
        ordering = ["created"]  # will suffice initially for most models


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

    class Meta(UUIDTimestampsModel.Meta):  # Django will set abstract=False.
        constraints = [
            models.UniqueConstraint(
                Lower("text"),
                name="question_text_lower_unique",
                violation_error_message=_("Question already exists (lowercase match)"),
            ),
        ]


class BadSite(UUIDTimestampsModel):
    """
    Model representing a website known to be a fraud.
    """

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Name of the site or its company behind it"),
    )

    bad_type = models.CharField(
        max_length=50,
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
