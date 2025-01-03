from django.contrib import admin
from .models import *

class ToDoItemInline(admin.StackedInline):
    model = ToDoItem
    extra = 1  # Number of blank inlines to display by default
    fields = ['task', 'is_completed', 'due_date']
    readonly_fields = ['created_at', 'updated_at']  # Optional: Make timestamps read-only
    show_change_link = True  # Optional: Allows clicking to edit in detail view

@admin.register(ToDoList)
class ToDoListAdmin(admin.ModelAdmin):
    list_display = ['company_owner', 'title', 'created_at', 'updated_at']
    search_fields = ['title', 'company_owner__username']  # Enable search by list name and owner
    list_filter = ['company_owner', 'updated_at']  # Filter options in admin
    inlines = [ToDoItemInline]
    

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['subject', 'client', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['subject', 'client__name', 'client__email']

