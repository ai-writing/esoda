# This Python file uses the following encoding: utf-8

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationFormUniqueEmail

from django import forms


FIELDS = [(1, 'High Performance Computing'), (2, 'Computer Network'), (3, 'Net and Information Security'),
          (4, 'Software Engineering'), (5, 'Database and Data Mining'), (6, 'Theoretical Computer Science'),
          (7, 'Computer Graphics and Multimedia'), (8, 'Artificial Intelligence and Pattern Recognition'),
          (9, 'Human-Computer Interaction and Pervasive Computing'), (10, 'New'), (0, 'bnc')]

FIELD_NAME = [(1, u'高性能计算'), (2, u'计算机网络'), (3, u'网络安全'), (4, u'软件工程'), (5, u'数据挖掘'),
              (6, u'计算机理论'), (7, u'计算机图形学'), (8, u'人工智能'), (9, u'人机交互'), (10, u'交叉综合'),
              (0, u'BNC'), (11, u'全部')]


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
