from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    priority = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(priority__gt=0), name="priority_gt_0")
        ]

    def __str__(self):
        return self.title
