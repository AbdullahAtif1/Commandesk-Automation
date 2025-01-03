from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from profiles.models import Client
from django.utils.timezone import is_naive, make_aware, now
from django.core.exceptions import ValidationError

class ToDoList(models.Model):
    company_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="to_do_lists",
        verbose_name="Company Owner"
    )
    title = models.CharField(max_length=255, verbose_name="List Title")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    def __str__(self):
        return f"{self.title} (Owner: {self.company_owner.username})"

    class Meta:
        verbose_name = "To-Do List"
        verbose_name_plural = "To-Do Lists"
        ordering = ['-created_at']


class ToDoItem(models.Model):
    to_do_list = models.ForeignKey(
        ToDoList,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="To-Do List"
    )
    task = models.CharField(max_length=255, verbose_name="Task Description")
    is_completed = models.BooleanField(default=False, verbose_name="Completed")
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Due Date")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")
    
    def clean(self):
        if self.due_date and is_naive(self.due_date):
            raise ValidationError("Due date must be timezone-aware.")

    def save(self, *args, **kwargs):
        if self.due_date and is_naive(self.due_date):
            self.due_date = make_aware(self.due_date)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.task} - {'Completed' if self.is_completed else 'Pending'}"

    class Meta:
        verbose_name = "To-Do Item"
        verbose_name_plural = "To-Do Items"
        ordering = ['is_completed', 'due_date', '-created_at']
        constraints = [
            models.UniqueConstraint(fields=['to_do_list', 'task'], name='unique_task_per_list')
        ]


class Complaint(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='complaints',
        verbose_name=_("Client"),
        help_text=_("The client who raised this complaint.")
    )
    company_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="complaints",
        verbose_name=_("Company Owner"),
        help_text=_("The owner of the company handling this complaint.")
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_("Subject"),
        help_text=_("Brief description of the complaint.")
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Detailed information about the complaint.")
    )
    status_choices = [
        ("new", _("New")),
        ("in_progress", _("In Progress")),
        ("resolved", _("Resolved")),
        ("closed", _("Closed")),
    ]
    status = models.CharField(
        max_length=20,
        choices=status_choices,
        default="new",
        verbose_name=_("Status"),
        help_text=_("Current status of the complaint.")
    )
    resolution_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Resolution Notes"),
        help_text=_("Notes or actions taken to resolve the complaint.")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"{self.subject} - {self.client.name}"

    class Meta:
        verbose_name = _("Complaint")
        verbose_name_plural = _("Complaints")
        ordering = ["updated_at"]



