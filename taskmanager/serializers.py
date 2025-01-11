from rest_framework import serializers
from .models import Task, DeadlineExtensionLog, User
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings


class UserDropDownSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']


class TaskDropDownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']


class SubtaskSerializer(serializers.ModelSerializer):
    subtasks = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'name', 'status', 'due_date', 'assigned_to', 'parent_task', 'subtasks']

    def get_subtasks(self, obj):
        # Recursively fetch subtasks of the current subtask
        subtasks = Task.objects.filter(parent_task=obj)
        return SubtaskSerializer(subtasks, many=True).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['assigned_to'] = UserDropDownSerializer(instance.assigned_to).data
        return representation


class TaskSerializer(serializers.ModelSerializer):
    subtasks = SubtaskSerializer(many=True, read_only=True)  # Subtasks will be nested and read-only for GET requests

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'priority', 'status', 'due_date', 'assigned_to', 'assigned_by', 
                  'created_at', 'updated_at', 'parent_task', 'subtasks']
        read_only_fields = ['created_at', 'assigned_by', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['assigned_to'] = UserDropDownSerializer(instance.assigned_to).data
        representation['assigned_by'] = UserDropDownSerializer(instance.assigned_by).data
        return representation

    def validate(self, data):
        # Rule 2: A task's due_date cannot be earlier than its dependency's due_date
        if data.get('parent_task'):
            parent_task = data['parent_task']
            if data['due_date'] > parent_task.due_date:
                raise serializers.ValidationError(f"Due date cannot be earlier than the due date of the parent task: {parent_task.due_date}")

        return data
    
    def update(self, instance, validated_data):
        status = validated_data.get('status', instance.status)

        # Validation rule: A task's status cannot be changed from Pending to Completed without being In Progress
        if status == 'Completed' and instance.status != 'In Progress':
            raise serializers.ValidationError("A task must be In Progress before it can be marked as Completed.")
        
        # Rule 1: A task can only be marked Completed if all its dependencies are completed
        if status == 'Completed':
            parent_task = instance.parent_task
            if parent_task and parent_task.status != 'Completed':
                raise serializers.ValidationError(f"A task can only be marked as Completed if all its dependencies are completed. Parent task '{parent_task.name}' is not completed yet.")

        # Proceed with the regular update process
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class DeadlineExtensionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeadlineExtensionLog
        fields = ['id', 'task', 'request_by', 'new_deadline', 'reason', 'status', 'created_at', 'approved_by', 'approved_at']
        read_only_fields = ['status', 'request_by', 'approved_by', 'approved_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['task'] = TaskDropDownSerializer(instance.task).data
        return representation

    def validate(self, data):
        task = data['task']
        new_deadline = data['new_deadline']

        # Rule 3: A task can have a maximum of 3 deadline extensions
        if task.extension_logs.count() >= 3:
            raise serializers.ValidationError({"task": "A task can have a maximum of 3 deadline extensions."})

        # Rule 4: The new due date must be after the current due date
        if new_deadline <= task.due_date:
            raise serializers.ValidationError("New due date must be after the current due date.")
        
        return data


class DeadlineExtensionApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeadlineExtensionLog
        fields = ['id', 'task', 'new_deadline', 'status', 'approved_at']
        read_only_fields = ['task', 'new_deadline', 'approved_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['task'] = TaskDropDownSerializer(instance.task).data
        return representation

    def update(self, instance, validated_data):
        status = validated_data.get('status', instance.status)

        # Rule 5: An extension request can only be approved or rejected by the task's assigned_to user
        if status in ['APPROVED', 'REJECTED'] and self.context['request'].user != instance.task.assigned_by:
            raise serializers.ValidationError("Only the assigned user can approve or reject a deadline extension request.")
        
        # Update fields 
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if status == "APPROVED":
            instance.approved_at = now()
            task = instance.task
            task.due_date = instance.new_deadline  # Update the task's deadline
            task.save()

        instance.save()

        self._send_email(instance, status)
        
        return instance

    def _send_email(self, extension_request, action):
        """
        Send an email notification about the approval or rejection.
        """
        task = extension_request.task
        developer_email = extension_request.request_by.email

        subject = f"Deadline Extension {action.capitalize()} for Task: {task.name}"
        if action == "APPROVED":
            message = (
                f"The deadline extension for task '{task.name}' has been approved.\n\n"
                f"New Deadline: {extension_request.new_deadline}"
            )
        else:
            message = f"The deadline extension for task '{task.name}' has been rejected."

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [developer_email])






class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ("username", "password")
