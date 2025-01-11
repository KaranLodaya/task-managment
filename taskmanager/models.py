from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
# from django.contrib.auth.models import AbstractUser


# class User(AbstractUser):
#     is_manager = models.BooleanField(default=False)  # Add a flag for managerial users


class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('When Free', 'When Free'),  # lowest priority
        ('Next Week', 'Next Week'),
        ('ASAP', 'ASAP'),
        ('URGENT', 'URGENT'),  # highest priority
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='When Free')
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    deadline_extension_logs = models.ManyToManyField('DeadlineExtensionLog', blank=True, related_name='tasks_with_extension')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='tasks_assigned')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_tasks")


    def __str__(self):
        return self.name
    
    





class DeadlineExtensionLog(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='extension_logs')
    reason = models.TextField()  # Reason for the extension
    new_deadline = models.DateField()
    request_by = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='request')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by= models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='approvals')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Deadline extension request by {self.request_by.username} for {self.task.name} - {self.status}"


