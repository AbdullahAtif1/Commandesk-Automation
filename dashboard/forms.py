from django import forms
from .models import ToDoList, ToDoItem

class ToDoListForm(forms.ModelForm):
    class Meta:
        model = ToDoList
        fields = ['title']

class ToDoItemInlineForm(forms.ModelForm):
    class Meta:
        model = ToDoItem
        fields = ['task', 'is_completed', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
