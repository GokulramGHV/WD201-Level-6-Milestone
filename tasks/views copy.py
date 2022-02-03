# Add your Views Here
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic.base import TemplateView, RedirectView
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


class GenericCompleteTaskView(AuthorisedTaskManager, TemplateView, SingleObjectMixin):

    success_url = "/tasks"
    template_name = "task_complete.html"

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
    # queryset = Task.objects.filter(deleted=False, user=self.request.user)
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


class GenericTaskCreateView(LoginRequiredMixin, CreateView):
    form_class = TaskCreateForm
    template_name = "task_create.html"
    success_url = "/tasks"

    def GetPriorityList(self):
        prior_lst = []
        query = Task.objects.filter(deleted=False, user=self.request.user).order_by(
            "priority"
        )
        for obj in query:
            prior_lst.append(obj.priority)
        return prior_lst

    def GetIdList(self):
        id_lst = []
        query = Task.objects.filter(deleted=False, user=self.request.user).order_by(
            "priority"
        )
        for obj in query:
            id_lst.append(obj.id)
        return id_lst

    def UpdatePriorities(self, prior_lst, prior, id_prior):
        # prior_lst_old = self.GetPriorityList()
        id_lst = self.GetIdList()
        print("prior:", prior)
        # prior_lst.remove(prior)
        id_lst.remove(id_prior)
        print("id_lst(r):", id_lst)
        print("prior_lst(r):", prior_lst)
        for i in range(len(id_lst)):
            Task.objects.filter(id=id_lst[i]).update(priority=prior_lst[i])

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        prior = self.object.priority
        prior_lst = self.GetPriorityList()
        self.object.save()
        print("list - bef:", prior_lst)
        if prior in prior_lst:
            while prior in prior_lst:
                prior += 1
            prior_lst.append(prior)
            prior_lst.remove(self.object.priority)
            prior_lst.sort()
            self.UpdatePriorities(prior_lst, self.object.priority, self.object.id)
        print("lst - af:", prior_lst)

        return HttpResponseRedirect(self.get_success_url())


class GenericTaskUpdateView(AuthorisedTaskManager, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_update.html"
    success_url = "/tasks"

    def GetPriorityList(self):
        prior_lst = []
        query = Task.objects.filter(deleted=False, user=self.request.user).order_by(
            "priority"
        )
        for obj in query:
            prior_lst.append(obj.priority)
        return prior_lst

    def GetIdList(self):
        id_lst = []
        query = Task.objects.filter(deleted=False, user=self.request.user).order_by(
            "priority"
        )
        for obj in query:
            id_lst.append(obj.id)
        return id_lst

    def UpdatePriorities(self, prior_lst, prior, id_prior):
        id_lst = self.GetIdList()
        print("prior:", prior)
        prior_lst.remove(prior)
        id_lst.remove(id_prior)
        print("id_lst(r):", id_lst)
        print("prior_lst(r):", prior_lst)
        for i in range(len(id_lst)):
            Task.objects.filter(id=id_lst[i]).update(priority=prior_lst[i])

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        prior = self.object.priority
        prior_lst = self.GetPriorityList()
        self.object.save()
        print("list - bef:", prior_lst)
        if prior in prior_lst:
            while prior in prior_lst:
                prior += 1
            prior_lst.append(prior)
            prior_lst.remove(self.object.priority)
            prior_lst.sort()
            self.UpdatePriorities(prior_lst, self.object.priority, self.object.id)
        print("lst - af:", prior_lst)

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


# Function Based Views
def tasks_view(request):
    search_term = request.GET.get("search")
    tasks = Task.objects.filter(deleted=False).filter(completed=False)
    if search_term:
        tasks = (
            Task.objects.filter(title__icontains=search_term)
            .filter(deleted=False)
            .filter(completed=False)
        )

    return render(request, "tasks.html", {"tasks": tasks})


def completed_tasks_view(request):
    completed_tasks = Task.objects.filter(completed=True)
    return render(request, "completed.html", {"tasks": completed_tasks})


def add_task_view(request):
    task_val = request.GET.get("task")
    Task(title=task_val).save()
    return HttpResponseRedirect("/tasks")


def delete_task_view(request, idx):
    Task.objects.filter(id=idx).update(deleted=True)
    return HttpResponseRedirect("/tasks")


def complete_task_view(request, idx):
    Task.objects.filter(id=idx).update(completed=True)
    return HttpResponseRedirect("/tasks")


def all_tasks_view(request):
    tasks = Task.objects.filter(deleted=False).filter(completed=False)
    completed_tasks = Task.objects.filter(completed=True)
    return render(
        request, "all_tasks.html", {"pending": tasks, "completed": completed_tasks}
    )
