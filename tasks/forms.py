from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from tasks.models import Task

input_field_style = "bg-slate-100 w-full my-1 rounded-lg border-slate-100  shadow-inner px-4 py-3 focus:border-red-500 active:border-red-500 focus:ring-red-500 checked:bg-red-500"
check_box_style = "h-6 w-6 rounded border-slate-100  shadow-inner border-none bg-slate-100 checked:bg-red-500 text-red-500 focus:ring-red-500"

class TaskCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TaskCreateForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            try:
                if visible.field.widget.input_type == "checkbox":
                    visible.field.widget.attrs[
                        "class"
                    ] = check_box_style
                else:
                    visible.field.widget.attrs["class"] = input_field_style
            except:
                visible.field.widget.attrs["class"] = input_field_style

    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 5:
            raise ValidationError("Title too small, must be greater than 5 characters!")
        return title.capitalize()

    def clean_priority(self):
        priority = self.cleaned_data["priority"]
        if priority <= 0:
            raise ValidationError("Prioriry must be greater than zero!")
        return priority

    class Meta:
        model = Task
        fields = ["title", "description", "priority", "completed"]


class CustomUserCreateForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreateForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = input_field_style

class CustomUserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserLoginForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = input_field_style
