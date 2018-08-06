"""
Serilizers for the FOIA application API
"""

# Django
from django.contrib.auth.models import User
from django.utils.timezone import get_default_timezone

# Third Party
from rest_framework import permissions, serializers

# MuckRock
from muckrock.agency.models import Agency
from muckrock.foia.models import (
    FOIACommunication,
    FOIAFile,
    FOIANote,
    FOIARequest,
)


class DateTimeField(serializers.DateTimeField):
    """Custom formatting for date time fields"""

    def to_representation(self, value):
        """Display dates how we used to, as naive times in the local timezone"""
        return (
            value.astimezone(get_default_timezone()).replace(tzinfo=None)
            .isoformat()
        )


class FOIAPermissions(permissions.DjangoModelPermissionsOrAnonReadOnly):
    """
    Object-level permission to allow owners of an object partially update it
    Also allows authenticated users to submit requests
    Assumes the model instance has a `user` attribute.
    """

    def has_permission(self, request, view):
        """Allow authenticated users to submit requests and update their own requests"""
        if request.user.is_authenticated() and request.method in [
            'POST', 'PATCH'
        ]:
            return True
        return super(FOIAPermissions, self).has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """Grant permission?"""
        # Instance must have an attribute named `user`.
        if obj.has_perm(request.user, 'change') and request.method == 'PATCH':
            return True

        # check non-object has permission here if the user doesn't own the object
        return super(FOIAPermissions, self).has_permission(request, view)


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to allow access only to owners of an object
    """

    def has_object_permission(self, request, view, obj):
        """Grant permission?"""
        # Instance must have an attribute named `user`.
        return obj.has_perm(request.user, 'change')


class FOIAFileSerializer(serializers.ModelSerializer):
    """Serializer for FOIA File model"""
    ffile = serializers.CharField(source='ffile.url', read_only=True)
    datetime = DateTimeField()

    class Meta:
        model = FOIAFile
        exclude = ('comm',)


class FOIACommunicationSerializer(serializers.ModelSerializer):
    """Serializer for FOIA Communication model"""
    files = FOIAFileSerializer(many=True)
    foia = serializers.PrimaryKeyRelatedField(
        queryset=FOIARequest.objects.all(),
        style={
            'base_template': 'input.html'
        }
    )
    likely_foia = serializers.PrimaryKeyRelatedField(
        queryset=FOIARequest.objects.all(),
        style={
            'base_template': 'input.html'
        }
    )
    delivered = serializers.SerializerMethodField()
    resolved_by = serializers.SerializerMethodField()
    datetime = DateTimeField()

    def __init__(self, *args, **kwargs):
        super(FOIACommunicationSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request is None:
            self.fields.pop('resolved_by')
        elif not request.user.is_staff:
            self.fields.pop('resolved_by')

    def get_delivered(self, obj):
        """Get how the communication was delivered"""
        return obj.get_delivered()

    def get_resolved_by(self, obj):
        """Get who resolved the response task"""
        tasks = obj.responsetask_set.all()
        if tasks and tasks[0].resolved_by:
            return tasks[0].resolved_by.username
        else:
            return None

    class Meta:
        model = FOIACommunication
        fields = [
            'foia',
            'from_user',
            'to_user',
            'subject',
            'datetime',
            'response',
            'autogenerated',
            'thanks',
            'full_html',
            'communication',
            'status',
            'likely_foia',
            'files',
            'delivered',
            'resolved_by',
        ]


class FOIANoteSerializer(serializers.ModelSerializer):
    """Serializer for FOIA Note model"""
    datetime = DateTimeField(read_only=True)

    class Meta:
        model = FOIANote
        exclude = ('id', 'foia')


class FOIARequestSerializer(serializers.ModelSerializer):
    """Serializer for FOIA Request model"""
    username = serializers.StringRelatedField(source='composer.user')
    user = serializers.PrimaryKeyRelatedField(
        source='composer.user',
        queryset=User.objects.all(),
        style={'base_template': 'input.html'},
    )
    agency = serializers.PrimaryKeyRelatedField(
        queryset=Agency.objects.all(),
        style={'base_template': 'input.html'},
    )
    tags = serializers.StringRelatedField(many=True)
    communications = FOIACommunicationSerializer(many=True)
    notes = FOIANoteSerializer(many=True)
    absolute_url = serializers.ReadOnlyField(source='get_absolute_url')
    tracking_id = serializers.ReadOnlyField(source='current_tracking_id')
    datetime_submitted = DateTimeField(
        read_only=True, source='composer.datetime_submitted'
    )
    datetime_done = DateTimeField()

    def __init__(self, *args, **kwargs):
        # pylint: disable=super-on-old-class
        super(FOIARequestSerializer, self).__init__(*args, **kwargs)
        if self.instance and isinstance(self.instance, FOIARequest):
            foia = self.instance
        else:
            foia = None

        request = self.context.get('request', None)
        if request is None:
            self.fields.pop('mail_id')
            self.fields.pop('email', None)
            self.fields.pop('notes')
            return
        if not request.user.is_staff:
            self.fields.pop('mail_id')
            self.fields.pop('email', None)
            if not foia:
                self.fields.pop('notes')
            else:
                has_change = foia.has_perm(request.user, 'change')
                if not has_change:
                    self.fields.pop('notes')
                if request.method == 'PATCH':
                    self._set_patch_fields(request.user, foia)

    def _set_patch_fields(self, user, foia):
        """Set which fields the user may PATCH"""
        has_change = foia.has_perm(user, 'change')
        has_embargo = foia.has_perm(user, 'embargo')
        has_embargo_perm = foia.has_perm(user, 'embargo_perm')
        allowed = []
        if has_change:
            allowed.extend(['notes', 'tags'])
        if has_embargo:
            allowed.append('embargo')
        if has_embargo_perm:
            allowed.append('permanent_embargo')
        for field in self.fields.keys():
            if field not in allowed:
                self.fields.pop(field)

    class Meta:
        model = FOIARequest
        fields = (
            # request details
            'id',
            'title',
            'slug',
            'status',
            'embargo',
            'permanent_embargo',
            'user',
            'username',
            'agency',
            # request dates
            'datetime_submitted',
            'date_due',
            'days_until_due',
            'date_followup',
            'datetime_done',
            'date_embargo',
            # processing details
            'mail_id',
            'tracking_id',
            'price',
            'disable_autofollowups',
            # connected models
            'tags',
            'notes',
            'communications',
            # computed fields
            'absolute_url',
        )
