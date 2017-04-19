from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationFormUniqueEmail


class RegistrationFormEmailAsUsername(RegistrationFormUniqueEmail):
    """
    Subclass of ``RegistrationFormUniqueEmail`` which enforces uniqueness of
    email addresses and copies the email to username field.
    """

    def __init__(self, *args, **kwargs):
        query_dict = kwargs.get('data')
        if query_dict:
            query_dict = query_dict.copy()
            query_dict.update({'username': query_dict.get('email')})
            kwargs.update({'data': query_dict})
        super(RegistrationFormUniqueEmail, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'autofocus': True})
