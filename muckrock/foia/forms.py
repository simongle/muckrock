"""
Forms for FOIA application
"""

from django import forms

import autocomplete_light
import inspect
import sys
from datetime import datetime, date, timedelta

from muckrock.agency.models import Agency, AgencyType
from muckrock.foia.models import FOIARequest, FOIAMultiRequest, FOIAFile, FOIANote
from muckrock.foia.utils import make_template_choices
from muckrock.foia.validate import validate_date_order
from muckrock.jurisdiction.models import Jurisdiction


class FOIARequestForm(forms.ModelForm):
    """A form for a FOIA Request"""
    agency = forms.ModelChoiceField(
        label='Agency',
        required=False,
        queryset=Agency.objects.order_by('name'),
        widget=forms.Select(attrs={'class': 'combobox'}),
        help_text=('Select one of the agencies for the jurisdiction you '
                   'have chosen, or write in the correct agency if known.')
    )    
    embargo = forms.BooleanField(
        required=False,
        help_text=('Embargoing a request keeps it completely private from '
                   'other users until the embargo date you set. '
                   'You may change this whenever you want.')
    )
    request = forms.CharField(
        widget=forms.Textarea(attrs={'style': 'width:450px; height:200px;'})
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(FOIARequestForm, self).__init__(*args, **kwargs)
        if not (self.request and self.request.user.get_profile().can_embargo()):
            del self.fields['embargo']
            self.Meta.fields = ['title', 'agency']

    class Meta:
        # pylint: disable=R0903
        model = FOIARequest
        fields = ['title', 'agency', 'embargo']
        widgets = {
            'title': forms.TextInput(attrs={'style': 'width:450px;'}),
        }

class FOIAMultiRequestForm(forms.ModelForm):
    """A form for a FOIA Multi-Request"""

    embargo = forms.BooleanField(required=False,
                                 help_text='Embargoing a request keeps it completely private from '
                                           'other users until the embargo date you set.  '
                                           'You may change this whenever you want.')
    requested_docs = forms.CharField(label='Request',
        widget=forms.Textarea(attrs={'style': 'width:450px; height:50px;'}))

    class Meta:
        # pylint: disable=R0903
        model = FOIAMultiRequest
        fields = ['title', 'embargo', 'requested_docs']
        widgets = {'title': forms.TextInput(attrs={'style': 'width:450px;'})}

class FOIAEmbargoForm(forms.ModelForm):
    """A form to update the embargo status of a FOIA Request"""

    embargo = forms.BooleanField(required=False,
                                 help_text='Embargoing a request keeps it completely private from '
                                           'other users until the embargo date you set.  '
                                           'You may change this whenever you want.')

    class Meta:
        # pylint: disable=R0903
        model = FOIARequest
        fields = ['embargo']

class FOIAEmbargoDateForm(FOIAEmbargoForm):
    """A form to update the embargo status of a FOIA Request"""

    date_embargo = forms.DateField(label='Embargo date', required=False,
                                   widget=forms.TextInput(attrs={'class': 'datepicker'}))

    def clean(self):
        """date_embargo is required if embargo is checked and must be within 30 days"""

        embargo = self.cleaned_data.get('embargo')
        date_embargo = self.cleaned_data.get('date_embargo')

        if embargo:
            if not date_embargo:
                self._errors['date_embargo'] = self.error_class(
                        ['Embargo date is required if embargo is selected'])
            elif date_embargo > date.today() + timedelta(30):
                self._errors['date_embargo'] = self.error_class(
                        ['Embargo date must be within 30 days of today'])

        return self.cleaned_data

    class Meta:
        # pylint: disable=R0903
        model = FOIARequest
        fields = ['embargo', 'date_embargo']

class FOIAMultipleSubmitForm(forms.Form):
    """Form to select multiple agencies to submit to"""

    agency_type = forms.ModelChoiceField(queryset=AgencyType.objects.all(), required=False)
    jurisdiction = forms.ModelChoiceField(queryset=Jurisdiction.objects.all(), required=False)

class AgencyConfirmForm(forms.Form):
    """Confirm agencies for a multiple submit"""

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset', [])
        super(AgencyConfirmForm, self).__init__(*args, **kwargs)
        self.fields['agencies'].queryset = self.queryset

    class AgencyChoiceField(forms.ModelMultipleChoiceField):
        """Add jurisdiction to agency label"""
        def label_from_instance(self, obj):
            return '%s - %s' % (obj.name, obj.jurisdiction)

    agencies = AgencyChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple)

class FOIADeleteForm(forms.Form):
    """Form to confirm deleting a FOIA Request"""

    confirm = forms.BooleanField(label='Are you sure you want to delete this FOIA request?',
                                 help_text='This cannot be undone!')

FOIAFileFormSet = forms.models.modelformset_factory(FOIAFile, fields=('ffile',))

class FOIANoteForm(forms.ModelForm):
    """A form for a FOIA Note"""
    class Meta:
        # pylint: disable=R0903
        model = FOIANote
        fields = ['note']
        widgets = {'note': forms.Textarea()}

class FOIAAdminFixForm(forms.ModelForm):
    """Form to email from the request's address"""
    class Meta:
        model = FOIARequest
        fields = ['from_email', 'email', 'other_emails', 'comm']
    
    from_email = forms.CharField(
        label='From',
        required=False,
        help_text='Leaving blank will fill in with request owner.'
    )
    email = forms.EmailField(
        label='To',
        required=False,
        help_text='Leave blank to send to agency default.'
    )
    other_emails = forms.CharField(label='CC', required=False)
    comm = forms.CharField(label='Body', widget=forms.Textarea())
    snail_mail = forms.BooleanField(required=False, label='Snail Mail Only')

    

class FOIAWizardParent(forms.Form):
    """A form with generic options for every template"""
    agency = None
    agency_type = None

    @classmethod
    def get_agency(cls, jurisdiction):
        """Get the agency for this template given a jurisdiction"""

        def get_first(list_):
            """Get first element of a list or none if it is empty"""
            if list_:
                return list_[0]

        agency = None
        if cls.agency:
            try:
                agency = (Agency.objects.filter(name=cls.agency, jurisdiction=jurisdiction))[0]
            except IndeXError:
                print 'index error'
        if not agency and cls.agency_type:
            try:
                type = (AgencyType.objects.filter(name=cls.agency_type))[0]
            except IndexError:
                return None
            try:
                agency = (Agency.objects.filter(types=type, jurisdiction=jurisdiction))[0]
            except IndexError:
                return None

        return agency

class FOIABlankForm(FOIAWizardParent):
    title = forms.CharField(
        help_text='70 character limit',
        max_length=70,
        widget=forms.TextInput()
    )
    document_request = forms.CharField(
        help_text='Write one sentence specifically describing the document.',
        widget=forms.Textarea()
    )
    slug = 'none'
    name = 'Write My Own Request'
    category = 'None'
    level = 'lsf'
    agency_type = 'Clerk'

TEMPLATES = dict((form.slug, form) for form_name, form in inspect.getmembers(sys.modules[__name__],
                 lambda member: inspect.isclass(member) and issubclass(member, FOIAWizardParent))
                 if form is not FOIAWizardParent)
LOCAL_TEMPLATE_CHOICES = make_template_choices(TEMPLATES, 'l')
STATE_TEMPLATE_CHOICES = make_template_choices(TEMPLATES, 's')
FEDERAL_TEMPLATE_CHOICES = make_template_choices(TEMPLATES, 'f')

class FOIAWizardWhereForm(forms.Form):
    """A form to select the jurisdiction to file the request in"""
    level = forms.ChoiceField(widget=forms.CheckboxSelectMultiple, choices=(('federal', 'Federal'),
                                       ('state', 'State'),
                                       ('local', 'Local'),
                                       ('multi', 'Multiple Agencies')))
    state = autocomplete_light.ModelChoiceField('StateAutocomplete',
        queryset=Jurisdiction.objects.filter(level='s', hidden=False), required=False)
    local = autocomplete_light.ModelChoiceField('LocalAutocomplete',
        queryset=Jurisdiction.objects.filter(level='l', hidden=False).order_by('parent', 'name'),
        required=False)

    def clean(self):
        """Make sure state or local is required based off of choice of level"""

        level = self.cleaned_data.get('level')
        state = self.cleaned_data.get('state')
        local = self.cleaned_data.get('local')

        if level == 'state' and not state:
            self._errors['state'] = self.error_class(
                    ['State required if you choose to file at the state level'])

        if level == 'local' and not local:
            self._errors['local'] = self.error_class(
                    ['Local required if you choose to file at the local level'])

        return self.cleaned_data

class FOIAWhatLocalForm(forms.Form):
    """A form to select what template to use for a local request"""

    template = forms.ChoiceField(choices=LOCAL_TEMPLATE_CHOICES)

class FOIAWhatStateForm(forms.Form):
    """A form to select what template to use for a state request"""

    template = forms.ChoiceField(choices=STATE_TEMPLATE_CHOICES)

class FOIAWhatFederalForm(forms.Form):
    """A form to select what template to use for a federal request"""

    template = forms.ChoiceField(choices=FEDERAL_TEMPLATE_CHOICES)

