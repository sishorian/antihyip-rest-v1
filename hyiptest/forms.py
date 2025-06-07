from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import DomainNameValidator
from django.utils.translation import gettext_lazy as _


def validate_lowercase(value):
    if not value.islower():
        raise ValidationError(
            _("%(value)s is not a lowercase string"), params={"value": value}
        )


class SearchDomainForm(forms.Form):
    """
    Form for a user to search a website domain in the fraud database.
    """

    # TODO: override form field template to have classes for <label>.
    # Disable classes for other form elements for now.
    q = forms.CharField(
        min_length=5,
        max_length=100,
        validators=[
            DomainNameValidator(message=_("Enter a valid domain name")),
            validate_lowercase,
        ],
        label=_("Domain name"),
        # Is displayed between label and input
        # help_text=_(""),
    )
    # q.widget.attrs.update({"class": "form-control"})
