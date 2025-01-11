import django_filters
from .models import Task, DeadlineExtensionLog
from django.contrib.auth.models import User
import datetime

class TaskFilter(django_filters.FilterSet):
    
    status = django_filters.ChoiceFilter(
        choices=Task.STATUS_CHOICES,  # Use predefined choices
        lookup_expr='exact',  # Ensure exact matching
    )

    due_date = django_filters.DateFromToRangeFilter(
        label='Due Date Range',
        field_name='due_date', 
        lookup_expr='exact',
    )

    overdue = django_filters.BooleanFilter(
        label='Overdue',
        field_name='due_date',
        method='filter_overdue',
    )

    priority = django_filters.ChoiceFilter(
        choices=Task.PRIORITY_CHOICES,  # Use predefined choices
        lookup_expr='exact',  # Ensure exact matching
    )

    class Meta:
        model = Task
        fields = ['status', 'priority', 'due_date','overdue']


    def filter_overdue(self, queryset, name, value):
        if value:
            return queryset.filter(due_date__lt=datetime.date.today())
        return queryset


class DeadlineExtensionLogFilter(django_filters.FilterSet):
    task = django_filters.ModelChoiceFilter(
        queryset=DeadlineExtensionLog.objects.all(),
        lookup_expr='exact',
    )

    extended_by = django_filters.CharFilter(
        lookup_expr='icontains',
    )

    new_due_date = django_filters.DateFromToRangeFilter(
        label='New Due Date Range',
        field_name='new_due_date', 
        lookup_expr='exact',
    )

    class Meta:
        model = DeadlineExtensionLog
        fields = ['task', 'extended_by', 'new_due_date']

