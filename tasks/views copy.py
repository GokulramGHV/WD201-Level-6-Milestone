# Add your Views Here
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, DeleteView, DeletionMixin, UpdateView
from django.views.generic.list import ListView

from tasks.forms import *
from tasks.models import Task


base_query = Task.objects.filter(user=request.user)
active_tasks = base_qs.filter(deleted=False)
completed_tasks = active_tasks.filter(completed=True)


class RedirectRootToTasks(RedirectView):
    url = "/tasks"


class AuthorisedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user).order_by(
            "priority"
        )


class UserLoginView(LoginView):
    form_class = CustomUserLoginForm
    template_name = "user_login.html"


class UserCreateView(CreateView):
    form_class = CustomUserCreateForm
    template_name = "user_create.html"
    success_url = "/user/login"


class GenericCompleteTaskView(AuthorisedTaskManager, View, SingleObjectMixin):

    success_url = "/tasks"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        Task.objects.filter(id=self.object.id, user=self.request.user).update(
            completed=True
        )
        return HttpResponseRedirect(self.success_url)


class GenericAllTasksView(AuthorisedTaskManager, ListView):
    queryset = active_tasks
    template_name = "all_tasks.html"
    context_object_name = "tasks"
    paginate_by = 4

    def get_context_data(self, *args, **kwargs):
        context = super(GenericAllTasksView, self).get_context_data(*args, **kwargs)
        context["completed_count"] = completed_tasks.count()
        context["total_count"] = active_tasks.count()
        return context


class GenericTaskDeleteView(AuthorisedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"


class GenericTaskDetailView(AuthorisedTaskManager, DetailView):
    model = Task
    template_name = "task_detail.html"


def dup_elems(lst, element):
    """
    Returns a list of duplicate priority elements in the given list of Tasks
    """
    # return [x for x in lst if x.priority == element]
    return list(filter(lambda x: x.priority == element, lst))


@transaction.atomic
def TaskPriorityCheck(priority, user):
    """
    A function to check if any two tasks have the same priority
    if so, then cascade update the priorities such that no two tasks have the same priority
    """
    task_lst = list(
        Task.objects.select_for_update()
        .filter(
            deleted=False,
            user=user,
            completed=False,
            priority__gte=priority,
        )
        .order_by("created_date")
    )

    while True:
        dup_prior = dup_elems(
            task_lst, priority
        )  # Returns a list containing tasks with same priority
        if len(dup_prior) <= 1:
            break

        task_lst[task_lst.index(dup_prior[0])].priority += 1
        priority += 1

    Task.objects.bulk_update(task_lst, ["priority"])


class GenericTaskCreateView(LoginRequiredMixin, CreateView):
    form_class = TaskCreateForm
    template_name = "task_create.html"
    success_url = "/tasks"

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        priority = self.object.priority
        self.object.save()
        TaskPriorityCheck(priority, self.request.user)
        return HttpResponseRedirect(self.get_success_url())


class GenericTaskUpdateView(AuthorisedTaskManager, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_update.html"
    success_url = "/tasks"

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        priority = self.object.priority
        self.object.save()
        TaskPriorityCheck(priority, self.request.user)
        return HttpResponseRedirect(self.get_success_url())


class GenericCompletedTaskView(LoginRequiredMixin, ListView):
    queryset = completed_tasks.order_by("priority")
    template_name = "completed.html"
    context_object_name = "tasks"
    paginate_by = 4

    def get_context_data(self, *args, **kwargs):
        context = super(GenericCompletedTaskView, self).get_context_data(
            *args, **kwargs
        )
        context["completed_count"] = completed_tasks.count()
        context["total_count"] = active_tasks.count()
        return context


class GenericTaskView(LoginRequiredMixin, ListView):
    queryset = active_tasks.filter(completed=False)
    template_name = "tasks.html"
    context_object_name = "tasks"
    paginate_by = 4

    def get_context_data(self, *args, **kwargs):
        context = super(GenericTaskView, self).get_context_data(*args, **kwargs)
        context["completed_count"] = completed_tasks.count()
        context["total_count"] = active_tasks.count()
        return context
