from django import forms
from .models import ToDoList, ToDoItem, Complaint
from profiles.models import Client

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
        

class ComplaintForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(),
        empty_label="Select a client",  # Optional: Placeholder for the dropdown
        label="Client"
    )

    class Meta:
        model = Complaint
        fields = ['client', 'subject', 'description', 'status']
        widgets = {
            'status': forms.Select(),  # Dropdown for status choices
            'subject': forms.TextInput(),  # Input for subject
            'description': forms.Textarea(),  # Textarea for description
        }

