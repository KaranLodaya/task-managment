from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Task, DeadlineExtensionLog

@receiver(post_save, sender=Task)
def send_task_assignment_email(sender, instance, created, **kwargs):
    if created and instance.assigned_to:
        subject = f"New Task Assigned: {instance.name}"
        message = f"""
        Hello {instance.assigned_to.username},

        You have been assigned a new task: "{instance.name}".

        Details:
        - Description: {instance.description}
        - Due Date: {instance.due_date}
        - Created At: {instance.created_at}

        Please log in to the task manager app to view more details.

        Best regards,
        Task Manager Team
        """
        recipient_list = [instance.assigned_to.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)


@receiver(post_save, sender=DeadlineExtensionLog)
def send_deadline_extention_email(sender, instance, created, **kwargs):
    if created:
        subject = f"Task Deadline Extension Request by {instance.request_by}"
        message = f"""
        Hello,

        A deadline extension request has been made for the task "{instance.task.name}" by {instance.request_by.username}.
        The new due date is: {instance.new_deadline}.
        Reason: {instance.reason}
        Requested By: {instance.request_by.username}
        """ 
        recipient_list = ['karan.lodaya@weservecodes.com']
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

