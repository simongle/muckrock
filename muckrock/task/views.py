"""
Views for the Task application
"""
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator

from muckrock.foia.models import STATUS
from muckrock.task.models import Task, OrphanTask, SnailMailTask, NewAgencyTask, ResponseTask
from muckrock.views import MRFilterableListView

class TaskList(MRFilterableListView):
    """List of tasks"""
    title = 'Tasks'
    template_name = 'lists/task_list.html'
    model = Task

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        """Dispatch overriden to limit access"""
        return super(TaskList, self).dispatch(*args, **kwargs)

    def post(self, request):
        """Handle general cases for updating Task objects"""
        # every request should specify the task it is updating
        task_pk = request.POST.get('task')
        tasks_pks = request.POST.getlist('tasks')
        if task_pk or tasks_pks:
            if task_pk:
                tasks = [get_object_or_404(Task, pk=task_pk)]
            else:
                tasks = [get_object_or_404(Task, pk=each_pk) for each_pk in tasks_pks]
        else:
            return redirect('task-list')

        for task in tasks:
            # These actions are shared between all Task objects
            # resolve will either be True or None
            # the task will only resolve if True
            if request.POST.get('resolve'):
                task.resolve()
            if request.POST.get('assign'):
                user_pk = request.POST.get('assign')
                user = get_object_or_404(User, pk=user_pk)
                task.assign(user)

        orphan_task_post_handler(request, task_pk)
        snail_mail_task_post_handler(request, task_pk)
        new_agency_task_post_handler(request, task_pk)
        response_task_post_handler(request, task_pk)

        return redirect('task-list')

def orphan_task_post_handler(request, task_pk):
    """Special post handlers exclusive to OrphanTasks"""
    try:
        orphan_task = OrphanTask.objects.get(pk=task_pk)
    except OrphanTask.DoesNotExist:
        return

    if request.POST.get('move'):
        foia_pks = request.POST.get('move', '')
        foia_pks = foia_pks.split(', ')
        orphan_task.move(request, foia_pks)
    if request.POST.get('reject'):
        orphan_task.reject()

    return

def snail_mail_task_post_handler(request, task_pk):
    """Special post handlers exclusive to SnailMailTasks"""
    try:
        snail_mail_task = SnailMailTask.objects.get(pk=task_pk)
    except SnailMailTask.DoesNotExist:
        return
    if request.POST.get('status'):
        status = request.POST.get('status')
        if status in dict(STATUS):
            snail_mail_task.set_status(status)
    return

def new_agency_task_post_handler(request, task_pk):
    """Special post handlers exclusive to NewAgencyTasks"""
    try:
        new_agency_task = NewAgencyTask.objects.get(pk=task_pk)
    except NewAgencyTask.DoesNotExist:
        return
    if request.POST.get('approve'):
        new_agency_task.approve()
    if request.POST.get('reject'):
        new_agency_task.reject()
    return

def response_task_post_handler(request, task_pk):
    """Special post handlers exclusive to ResponseTask"""
    try:
        response_task = ResponseTask.objects.get(pk=task_pk)
    except ResponseTask.DoesNotExist:
        return
    if request.POST.get('status'):
        status = request.POST.get('status')
        if status in dict(STATUS):
            response_task.set_status(status)
    return

@user_passes_test(lambda u: u.is_staff)
def assign(request):
    """Assign a user to a task, AJAX style"""
    user_pk = request.POST.get('user')
    task_pk = request.POST.get('task')
    try:
        if user_pk == '0':
            user = None
        else:
            user = User.objects.get(pk=user_pk)
        task = Task.objects.get(pk=task_pk)
    except (User.DoesNotExist, Task.DoesNotExist):
        return HttpResponse("Error", content_type='text/plain')

    task.assigned = user
    task.save()
    return HttpResponse("OK", content_type='text/plain')
