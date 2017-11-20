"""
Views to display lists of FOIA requests
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView

from actstream.models import following

from muckrock.agency.models import Agency
from muckrock.foia.filters import (
    FOIARequestFilterSet,
    MyFOIARequestFilterSet,
    MyFOIAMultiRequestFilterSet,
    ProcessingFOIARequestFilterSet,
    AgencyFOIARequestFilterSet,
)
from muckrock.foia.models import (
    FOIARequest,
    FOIAMultiRequest,
    )
from muckrock.news.models import Article
from muckrock.project.models import Project
from muckrock.views import (
        class_view_decorator,
        MRFilterListView,
        MRSearchFilterListView,
        )


class RequestExploreView(TemplateView):
    """Provides a top-level page for exploring interesting requests."""
    template_name = 'foia/explore.html'

    def get_context_data(self, **kwargs):
        """Adds interesting data to the context for rendering."""
        context = super(RequestExploreView, self).get_context_data(**kwargs)
        user = self.request.user
        visible_requests = FOIARequest.objects.get_viewable(user)
        context['top_agencies'] = (
            Agency.objects
            .get_approved()
            .annotate(foia_count=Count('foiarequest'))
            .order_by('-foia_count')
        )[:9]
        context['featured_requests'] = (
            visible_requests
            .filter(featured=True)
            .order_by('featured')
            .select_related_view()
        )
        context['recent_news'] = (
            Article.objects
            .get_published()
            .annotate(foia_count=Count('foias'))
            .exclude(foia_count__lt=2)
            .exclude(foia_count__gt=9)
            .prefetch_related(
                'authors',
                'foias',
                'foias__user',
                'foias__user__profile',
                'foias__agency',
                'foias__agency__jurisdiction',
                'foias__jurisdiction__parent__parent')
            .order_by('-pub_date')
        )[:3]
        context['featured_projects'] = (
            Project.objects
            .get_visible(user)
            .filter(featured=True)
            .prefetch_related(
                'requests',
                'requests__user',
                'requests__user__profile',
                'requests__agency',
                'requests__agency__jurisdiction',
                'requests__jurisdiction__parent__parent')
        )
        context['recently_completed'] = (
            visible_requests
            .get_done()
            .order_by('-date_done', 'pk')
            .select_related_view()
            .get_public_file_count(limit=5))
        context['recently_rejected'] = (
            visible_requests
            .filter(status__in=['rejected', 'no_docs'])
            .order_by('-date_updated', 'pk')
            .select_related_view()
            .get_public_file_count(limit=5))
        return context


class RequestList(MRSearchFilterListView):
    """Base list view for other list views to inherit from"""
    model = FOIARequest
    filter_class = FOIARequestFilterSet
    title = 'All Requests'
    template_name = 'foia/list.html'
    default_sort = 'date_updated'
    default_order = 'desc'
    sort_map = {
            'title': 'title',
            'user': 'user__first_name',
            'agency': 'agency__name',
            'jurisdiction': 'jurisdiction__name',
            'date_updated': 'date_updated',
            'date_submitted': 'date_submitted',
            }

    def get_queryset(self):
        """Limits requests to those visible by current user"""
        objects = super(RequestList, self).get_queryset()
        objects = objects.select_related_view()
        return objects.get_viewable(self.request.user)


@class_view_decorator(login_required)
class MyRequestList(RequestList):
    """View requests owned by current user"""
    filter_class = MyFOIARequestFilterSet
    title = 'Your Requests'
    template_name = 'foia/my_list.html'

    def get_queryset(self):
        """Limit to just requests owned by the current user."""
        queryset = super(MyRequestList, self).get_queryset()
        return queryset.filter(user=self.request.user)


@class_view_decorator(user_passes_test(
    lambda u: u.is_authenticated and u.profile.acct_type == 'agency'))
class AgencyRequestList(RequestList):
    """View requests owned by current agency"""
    filter_class = AgencyFOIARequestFilterSet
    title = "Your Agency's Requests"
    template_name = 'foia/agency_list.html'

    def get_queryset(self):
        """Requests owned by the current agency that they can respond to."""
        queryset = super(AgencyRequestList, self).get_queryset()
        return queryset.filter(
                agency=self.request.user.profile.agency,
                status__in=(
                    'ack',
                    'processed',
                    'appealing',
                    'fix',
                    'payment',
                    'partial',
                    ),
                )


@class_view_decorator(login_required)
class MyMultiRequestList(MRFilterListView):
    """View requests owned by current user"""
    model = FOIAMultiRequest
    filter_class = MyFOIAMultiRequestFilterSet
    title = 'Multirequests'
    template_name = 'foia/multirequest_list.html'

    def dispatch(self, *args, **kwargs):
        """Basic users cannot access this view"""
        if self.request.user.is_authenticated and not self.request.user.profile.is_advanced():
            err_msg = (
                'Multirequests are a pro feature. '
                '<a href="%(settings_url)s">Upgrade today!</a>' % {
                    'settings_url': reverse('accounts')
                }
            )
            messages.error(self.request, err_msg)
            return redirect('foia-mylist')
        return super(MyMultiRequestList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        """Limit to just requests owned by the current user."""
        queryset = super(MyMultiRequestList, self).get_queryset()
        return queryset.filter(user=self.request.user)


@class_view_decorator(login_required)
class FollowingRequestList(RequestList):
    """List of all FOIA requests the user is following"""
    title = 'Requests You Follow'

    def get_queryset(self):
        """Limits FOIAs to those followed by the current user"""
        queryset = super(FollowingRequestList, self).get_queryset()
        followed = [f.pk for f in following(self.request.user, FOIARequest)
                if f is not None]
        return queryset.filter(pk__in=followed)


class ProcessingRequestList(RequestList):
    """List all of the currently processing FOIA requests."""
    title = 'Processing Requests'
    filter_class = ProcessingFOIARequestFilterSet
    template_name = 'foia/processing_list.html'
    default_sort = 'date_processing'
    default_order = 'asc'
    sort_map = {
            'title': 'title',
            'date_submitted': 'date_submitted',
            'date_processing': 'date_processing',
            }

    def dispatch(self, *args, **kwargs):
        """Only staff can see the list of processing requests."""
        if not self.request.user.is_staff:
            raise Http404()
        return super(ProcessingRequestList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        """Apply select and prefetch related"""
        objects = super(ProcessingRequestList, self).get_queryset()
        return objects.prefetch_related('communications').filter(status='submitted')
