"""
Forms for the project application
"""

# Django
from django import forms

# Third Party
from autocomplete_light import shortcuts as autocomplete_light
from autocomplete_light.contrib.taggit_field import TaggitField, TaggitWidget
from dal import forward

# MuckRock
from muckrock.core import autocomplete
from muckrock.project.models import Project


class ProjectCreateForm(forms.ModelForm):
    """Form for the basic fields of a project."""

    tags = TaggitField(
        widget=TaggitWidget(
            "TagAutocomplete",
            attrs={
                "placeholder": "Search tags",
                "data-autocomplete-minimum-characters": 1,
            },
        ),
        help_text="Separate tags with commas.",
        required=False,
    )

    class Meta:
        model = Project
        fields = ["title", "summary", "image", "tags"]
        help_texts = {
            "summary": "A short description of the project and its goals.",
            "image": "Image should be large and high-resolution.",
        }


class ProjectUpdateForm(forms.ModelForm):
    """Form for updating a project instance"""

    tags = TaggitField(
        widget=TaggitWidget("TagAutocomplete", attrs={"placeholder": "Search tags"}),
        help_text="Separate tags with commas.",
        required=False,
    )

    class Meta:
        model = Project
        fields = [
            "title",
            "summary",
            "image",
            "tags",
            "description",
            "contributors",
            "requests",
            "articles",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"class": "prose-editor"}),
            "contributors": autocomplete.ModelSelect2Multiple(
                url="user-autocomplete", attrs={"data-placeholder": "Search for users"}
            ),
            "requests": autocomplete_light.MultipleChoiceWidget(
                "FOIARequestAutocomplete"
            ),
            "articles": autocomplete.ModelSelect2Multiple(
                url="article-autocomplete",
                attrs={"data-placeholder": "Search for articles"},
            ),
        }
        help_texts = {
            "title": "Changing the title will change the URL of your project."
        }


class ProjectPublishForm(forms.Form):
    """Form for publishing a project."""

    notes = forms.CharField(required=False, widget=forms.Textarea)


class ProjectManagerForm(forms.Form):
    """Form for managing a list of projects"""

    projects = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Project.objects.none(),
        widget=autocomplete.ModelSelect2Multiple(
            url="project-autocomplete",
            attrs={"placeholder": "Search for a project"},
            forward=(forward.Const(True, "manager"),),
        ),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(ProjectManagerForm, self).__init__(*args, **kwargs)
        self.fields["projects"].queryset = Project.objects.get_manager(user)
