"""
Digest objects for the messages app
"""

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from actstream.models import Action, user_stream
from datetime import datetime, timedelta
import logging

class Digest(EmailMultiAlternatives):
    """
    A digest describes a collection of activity over a duration, which
    is then rendered into an email and delivered at a scheduled interval.
    """
    text_template = None
    html_template = None
    interval = None
    activity = {
        'count': 0,
        'requests': None,
        'following': None
    }

    def __init__(self, user, **kwargs):
        """Initialize the notification"""
        super(Digest, self).__init__(**kwargs)
        if isinstance(user, User):
            self.user = user
            self.to = [user.email]
        else:
            raise TypeError('Digest requires a User to recieve it')
        self.activity = self.get_activity()
        context = self.get_context_data()
        text_email = render_to_string(self.get_text_template(), context)
        html_email = render_to_string(self.get_html_template(), context)
        self.from_email = 'MuckRock <info@muckrock.com>'
        self.bcc = ['diagnostics@muckrock.com']
        self.subject = self.get_subject()
        self.body = text_email
        self.attach_alternative(html_email, 'text/html')

    def get_activity(self):
        """Returns a list of activities to be sent in the email"""
        duration = self.get_duration()
        f_stream = self.get_foia_activity(duration)
        u_stream = user_stream(self.user).filter(timestamp__gte=duration)\
                                         .exclude(verb__icontains='following')
        self.activity['count'] = f_stream.count() + u_stream.count()
        self.activity['requests'] = f_stream
        self.activity['following'] = u_stream
        return self.activity

    def get_duration(self):
        if not self.interval:
            raise NotImplementedError('No interval specified.')
        if not isinstance(self.interval, timedelta):
            raise TypeError('Interval attribute must be a datetime.timedelta object.')
        return datetime.now() - self.interval

    def get_foia_activity(self, period):
        """Returns activity on requests owned by the user."""
        foia_stream = Action.objects.requests_for_user(self.user)
        foia_stream = foia_stream.filter(timestamp__gte=period)
        user_ct = ContentType.objects.get_for_model(self.user)
        # exclude actions where the user is the Actor
        # since they know which actions they've taken themselves
        foia_stream.exclude(actor_content_type=user_ct, actor_object_id=self.user.id)
        return foia_stream

    def get_context_data(self):
        """Segment and classify the activity"""
        context = {
            'user': self.user,
            'activity': self.activity,
            'base_url': 'https://www.muckrock.com'
        }
        return context

    def get_text_template(self):
        """Returns the text template"""
        if not self.text_template:
            raise NotImplementedError('No text template specified.')
        return self.text_template

    def get_html_template(self):
        """Returns the html template"""
        if not self.html_template:
            raise NotImplementedError('No HTML template specified.')
        return self.html_template

    def get_subject(self):
        """Summarizes the activities in the notification"""
        subject = str(self.activity['count']) + ' Update'
        if self.activity['count'] > 1:
            subject += 's'
        return subject

    def send(self, *args):
        """Don't send the email if there's no activity."""
        if self.activity['count'] < 1:
            return 0
        return super(Digest, self).send(*args)


class DailyDigest(Digest):
    """Sends a daily email digest"""
    text_template = 'message/notification/daily.txt'
    html_template = 'message/notification/daily.html'
    interval = timedelta(days=1)
