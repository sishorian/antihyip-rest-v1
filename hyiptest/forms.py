from django import forms
from django.core.validators import DomainNameValidator
from django.utils.translation import gettext_lazy as _


class DomainSearchForm(forms.Form):
    """
    Form for a user to search domain of a site in the fraud database.
    """

    domain = forms.CharField(
        min_length=5,
        max_length=100,
        validators=[DomainNameValidator(message=_("Enter a valid domain name"))],
        label=_("Domain name"),
        help_text=_("Enter the domain name of the site you want to check"),
    )
