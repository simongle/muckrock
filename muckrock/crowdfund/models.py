"""
Models for the crowdfund application
"""

from django.contrib.auth.models import User, AnonymousUser
from django.db import models

from datetime import date
from decimal import Decimal
import logging

from muckrock.foia.models import FOIARequest
from muckrock import task

class CrowdfundABC(models.Model):
    """Abstract base class for crowdfunding objects"""
    # pylint: disable=too-few-public-methods, model-missing-unicode
    class Meta:
        abstract = True

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    payment_capped = models.BooleanField(default=False)
    payment_required = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default='0.00'
    )
    payment_received = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default='0.00'
    )
    date_due = models.DateField()

    def expired(self):
        """Has this crowdfuning run out of time?"""
        return date.today() >= self.date_due

    def amount_remaining(self):
        """Reports the amount still needed to be raised"""
        return self.payment_required - self.payment_received

    def update_payment_received(self):
        """Combine the amounts of all the payments"""
        total_amount = Decimal()
        payments = self.payments.all()
        for payment in payments:
            logging.debug(payment)
            total_amount += payment.amount
        self.payment_received = total_amount
        self.save()
        if self.payment_received >= self.payment_required:
            self.complete_crowdfund()

    def complete_crowdfund(self):
        """Once the crowdfund reaches its goal: expire it, log it, and create a new task for it."""
        self.date_due = date.today()
        self.save()
        logging.info('Crowdfund %d reached its goal.', self.id)
        task.models.CrowdfundTask.objects.create(crowdfund=self)

    def contributors(self):
        """Return a list of all the contributors to a crowdfund"""
        contributors = []
        payments = self.payments.all()
        for payment in payments:
            if payment.show and payment.user:
                contributors.append(payment.user)
            else:
                contributors.append(AnonymousUser())
        logging.debug(payments)
        logging.debug(contributors)
        return contributors

    def anonymous_contributors(self):
        """Return anonymous contributors only."""
        return [x for x in self.contributors() if x.is_anonymous()]

    def named_contributors(self):
        """Return unique named contributors only."""
        # returns the list of a set of a list to remove duplicates
        return list(set([x for x in self.contributors() if not x.is_anonymous()]))

    def get_crowdfund_object(self):
        """Return the object being crowdfunded. Should be implemented by subclasses."""
        # pylint:disable=no-self-use
        return None

class CrowdfundPaymentABC(models.Model):
    """Abstract base class for crowdfunding objects"""
    # pylint: disable=too-few-public-methods, model-missing-unicode
    user = models.ForeignKey(User, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    show = models.BooleanField(default=False)

    class Meta:
        abstract = True

class CrowdfundRequest(CrowdfundABC):
    """Keep track of crowdfunding for a request"""
    foia = models.OneToOneField(FOIARequest, related_name='crowdfund')

    def __unicode__(self):
        # pylint: disable=no-member
        return u'Crowdfunding for %s' % self.foia.title

    @models.permalink
    def get_absolute_url(self):
        """The url for this object"""
        return ('crowdfund-request', [], {'pk': self.pk})

    def get_crowdfund_object(self):
        return self.foia

class CrowdfundRequestPayment(CrowdfundPaymentABC):
    """M2M intermediate model"""
    crowdfund = models.ForeignKey(CrowdfundRequest, related_name='payments')

    def __unicode__(self):
        # pylint: disable=no-member
        return u'Payment of $%.2f by %s on %s for %s' % \
            (self.amount, self.user, self.date.date(), self.crowdfund.foia)

class CrowdfundProject(CrowdfundABC):
    """A crowdfunding campaign for a project."""
    project = models.ForeignKey('project.Project', related_name='crowdfund')

    def __unicode__(self):
        # pylint: disable=no-member
        return u'Crowdfunding for %s' % self.project.title

    @models.permalink
    def get_absolute_url(self):
        """The url for this object"""
        return ('crowdfund-project', [], {'pk': self.pk})

    def get_crowdfund_object(self):
        return self.project

    def make_payment(self, amount, user=None):
        """Creates a payment for the crowdfund"""
        payment = CrowdfundProjectPayment.objects.create(
            amount=amount,
            crowdfund=self,
            user=user
        )
        payment.save()
        return payment

class CrowdfundProjectPayment(CrowdfundPaymentABC):
    """Individual payments made to a project crowdfund"""
    crowdfund = models.ForeignKey(CrowdfundProject, related_name='payments')

    def __unicode__(self):
        # pylint: disable=no-member
        return u'Payment of $%.2f by %s on %s for %s' % \
            (self.amount, self.user, self.date.date(), self.crowdfund.project)
