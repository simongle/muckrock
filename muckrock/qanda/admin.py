"""
Admin registration for Q&A models
"""

# Django
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User

# Third Party
from reversion.admin import VersionAdmin

# MuckRock
from muckrock.core import autocomplete
from muckrock.foia.models import FOIARequest
from muckrock.qanda.models import Answer, Question


class AnswerForm(forms.ModelForm):
    """Form with autocomplete for users"""

    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="user-autocomplete",
            attrs={"data-placeholder": "User?", "data-width": None},
        ),
    )

    class Meta:
        model = Answer
        fields = "__all__"


class QuestionForm(forms.ModelForm):
    """Form with autocomplete for user and foia"""

    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="user-autocomplete",
            attrs={"data-placeholder": "User?", "data-width": None},
        ),
    )
    foia = forms.ModelChoiceField(
        queryset=FOIARequest.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(
            url="foia-request-autocomplete",
            attrs={"data-placeholder": "FOIA?", "data-width": None},
        ),
    )

    class Meta:
        model = Question
        fields = "__all__"


class AnswerInline(admin.TabularInline):
    """Answer Inline Admin"""

    model = Answer
    form = AnswerForm
    extra = 1


class QuestionAdmin(VersionAdmin):
    """Quesiton Admin"""

    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "user", "date")
    search_fields = ("title", "question")
    inlines = [AnswerInline]
    form = QuestionForm


admin.site.register(Question, QuestionAdmin)
