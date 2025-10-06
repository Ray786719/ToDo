from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Todo

# Customize admin site headers
admin.site.site_header = "📋 Todo App Administration"
admin.site.site_title = "Todo Admin"
admin.site.index_title = "Welcome to Todo App Admin"

# Register your models here.

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = (
        'text', 
        'user', 
        'priority_badge', 
        'due_date', 
        'due_time',
        'completed_status', 
        'created_at'
    )
    list_filter = (
        'completed', 
        'priority', 
        'due_date', 
        'created_at',
        'user'
    )
    search_fields = ('text', 'user__username', 'user__first_name', 'user__last_name')
    ordering = ('-created_at',)
    date_hierarchy = 'due_date'
    
    # Organize fields in the detail view
    fieldsets = (
        ('Task Information', {
            'fields': ('user', 'text', 'completed')
        }),
        ('Scheduling', {
            'fields': ('due_date', 'due_time', 'priority'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    # Make timestamps read-only
    readonly_fields = ('created_at', 'updated_at')
    
    # Enable actions
    actions = ['mark_completed', 'mark_incomplete', 'set_high_priority', 'set_medium_priority', 'set_low_priority']
    
    def priority_badge(self, obj):
        """Display priority as colored badge"""
        colors = {
            'high': '#dc3545',
            'medium': '#ffc107', 
            'low': '#28a745'
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display().upper()
        )
    priority_badge.short_description = 'Priority'
    
    def completed_status(self, obj):
        """Display completion status with icons"""
        if obj.completed:
            return format_html('✅ <span style="color: #28a745;">Completed</span>')
        else:
            return format_html('⏳ <span style="color: #6c757d;">Pending</span>')
    completed_status.short_description = 'Status'
    
    # Custom actions
    def mark_completed(self, request, queryset):
        updated = queryset.update(completed=True, updated_at=timezone.now())
        self.message_user(request, f'{updated} todo(s) marked as completed.')
    mark_completed.short_description = '✅ Mark selected todos as completed'
    
    def mark_incomplete(self, request, queryset):
        updated = queryset.update(completed=False, updated_at=timezone.now())
        self.message_user(request, f'{updated} todo(s) marked as incomplete.')
    mark_incomplete.short_description = '⏳ Mark selected todos as incomplete'
    
    def set_high_priority(self, request, queryset):
        updated = queryset.update(priority='high', updated_at=timezone.now())
        self.message_user(request, f'{updated} todo(s) set to high priority.')
    set_high_priority.short_description = '🔴 Set priority to High'
    
    def set_medium_priority(self, request, queryset):
        updated = queryset.update(priority='medium', updated_at=timezone.now())
        self.message_user(request, f'{updated} todo(s) set to medium priority.')
    set_medium_priority.short_description = '🟡 Set priority to Medium'
    
    def set_low_priority(self, request, queryset):
        updated = queryset.update(priority='low', updated_at=timezone.now())
        self.message_user(request, f'{updated} todo(s) set to low priority.')
    set_low_priority.short_description = '🟢 Set priority to Low'
    
    # Custom view for statistics in changelist
    def changelist_view(self, request, extra_context=None):
        # Add statistics to the context
        extra_context = extra_context or {}
        
        # Get statistics
        total_todos = Todo.objects.count()
        completed_todos = Todo.objects.filter(completed=True).count()
        pending_todos = total_todos - completed_todos
        
        # Priority stats
        high_priority = Todo.objects.filter(priority='high').count()
        medium_priority = Todo.objects.filter(priority='medium').count() 
        low_priority = Todo.objects.filter(priority='low').count()
        
        # Overdue todos (past due date and not completed)
        today = timezone.now().date()
        overdue_todos = Todo.objects.filter(
            due_date__lt=today, 
            completed=False
        ).count()
        
        # Today's todos
        today_todos = Todo.objects.filter(due_date=today).count()
        
        extra_context.update({
            'total_todos': total_todos,
            'completed_todos': completed_todos,
            'pending_todos': pending_todos,
            'completion_rate': round((completed_todos / total_todos * 100) if total_todos > 0 else 0, 1),
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority,
            'overdue_todos': overdue_todos,
            'today_todos': today_todos,
        })
        
        return super().changelist_view(request, extra_context)
