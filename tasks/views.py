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


class GenericCompleteTaskView(AuthorisedTaskManager, View,SingleObjectMixin):

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
    template_name = "all_tasks.html"
    context_object_name = "tasks"
    paginate_by = 4

    def get_context_data(self, *args, **kwargs):
        context = super(GenericAllTasksView, self).get_context_data(*args, **kwargs)
        context["completed_count"] = Task.objects.filter(
            deleted=False, completed=True, user=self.request.user
        ).count()
        context["total_count"] = Task.objects.filter(
            deleted=False, user=self.request.user
        ).count()
        return context


class GenericTaskDeleteView(AuthorisedTaskManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"


class GenericTaskDetailView(AuthorisedTaskManager, DetailView):
    model = Task
    template_name = "task_detail.html"


@transaction.atomic
def TaskPriorityCheck(priority, user):
    '''
    A function to check if any two tasks have the same priority
    if so, then cascade update the priorities such that no two tasks have the same priority
    '''
    task_lst = (
        Task.objects.select_for_update()
        .filter(
            deleted=False,
            user=user,
            completed= False,
            priority__gte=priority,
        )
        .order_by("priority")
    )

    update_lst = []
    prev = 0
    for task in task_lst:
        try:
            if prev.priority == task.priority:
                prev.priority += 1
                update_lst.append(prev)
            else:
                prev = task
        except:
            prev = task

    Task.objects.bulk_update(update_lst, ["priority"])


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
    template_name = "completed.html"
    context_object_name = "tasks"
    paginate_by = 4

    def get_queryset(self):
        return Task.objects.filter(completed=True, user=self.request.user).order_by(
            "priority"
        )

    def get_context_data(self, *args, **kwargs):
        context = super(GenericCompletedTaskView, self).get_context_data(
            *args, **kwargs
        )
        context["completed_count"] = Task.objects.filter(
            deleted=False, completed=True, user=self.request.user
        ).count()
        context["total_count"] = Task.objects.filter(
            deleted=False, user=self.request.user
        ).count()
        return context


class GenericTaskView(LoginRequiredMixin, ListView):
    template_name = "tasks.html"
    context_object_name = "tasks"
    paginate_by = 4

    def get_context_data(self, *args, **kwargs):
        context = super(GenericTaskView, self).get_context_data(*args, **kwargs)
        context["completed_count"] = Task.objects.filter(
            deleted=False, completed=True, user=self.request.user
        ).count()
        context["total_count"] = Task.objects.filter(
            deleted=False, user=self.request.user
        ).count()
        return context

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        tasks = Task.objects.filter(
            deleted=False, completed=False, user=self.request.user
        ).order_by("priority")
        if search_term:
            tasks = Task.objects.filter(
                title__icontains=search_term,
                deleted=False,
                completed=False,
                user=self.request.user,
            ).order_by("priority")

        return tasks
