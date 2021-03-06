"""
Tests for PDF generation
"""

# Django
from django.test import TestCase

# Third Party
from nose.tools import eq_, ok_

# MuckRock
from muckrock.communication.models import MailCommunication
from muckrock.foia.factories import FOIACommunicationFactory
from muckrock.task.factories import SnailMailTaskFactory
from muckrock.task.pdf import LobPDF, SnailMailPDF


class PDFTests(TestCase):
    """Test PDF generation"""

    def test_snail_mail_prepare(self):
        """Generate a SnailMailPDF"""
        snail = SnailMailTaskFactory()
        pdf = SnailMailPDF(
            snail.communication, snail.category, snail.switch, snail.amount
        )
        prepared_pdf, page_count, files, mail = pdf.prepare()
        ok_(prepared_pdf)
        eq_(page_count, 1)
        eq_(files, [])
        ok_(isinstance(mail, MailCommunication))

    def test_lob_prepare(self):
        """Generate a LobPDF"""
        communication = FOIACommunicationFactory()
        pdf = LobPDF(communication, "n", False, 0)
        prepared_pdf, page_count, files, mail = pdf.prepare()
        ok_(prepared_pdf)
        eq_(page_count, 1)
        eq_(files, [])
        ok_(isinstance(mail, MailCommunication))
