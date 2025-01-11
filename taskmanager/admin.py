from django.contrib import admin
from taskmanager.models import Task, DeadlineExtensionLog

# Customizing the task admin
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'assigned_by', 'assigned_to', 'status', 'due_date']  # Columns to display
    list_filter = ['status', 'priority', 'due_date']  # Filters for the admin interface
    search_fields = ['name', 'description']  # Fields that can be searched
    ordering = ['due_date']  # Default ordering for tasks

    readonly_fields = ['assigned_by', 'assigned_to', 'status']  # Fields that developers shouldn't modify
    
    def get_queryset(self, request):
        # Restrict developers to only see their own tasks
        queryset = super().get_queryset(request)
        if request.user.groups.filter(name='Developer').exists():
            # Developers can only see tasks assigned to them
            return queryset.filter(assigned_to=request.user)
        return queryset

    def has_change_permission(self, request, obj=None):
        # Restrict change permissions for developers
        if obj and request.user.groups.filter(name='Developer').exists():
            # Developers cannot change the 'assigned_by', 'assigned_to', or 'status' fields
            return False
        return super().has_change_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        # For developers, make the relevant fields readonly
        if request.user.groups.filter(name='Developer').exists():
            return self.readonly_fields + ['name', 'due_date', 'priority']
        return self.readonly_fields

admin.site.register(Task, TaskAdmin)

# Customizing the DeadlineExtensionLog admin
class DeadlineExtensionLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'request_by', 'new_deadline', 'reason']
    list_filter = ['task', 'new_deadline']
    search_fields = ['task', 'request_by']
    ordering = ['new_deadline']

admin.site.register(DeadlineExtensionLog, DeadlineExtensionLogAdmin)  # Register the model
