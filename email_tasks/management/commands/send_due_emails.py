from django.utils.timezone import now
from sales.models import EmailTask, execute_email_tasks

def process_due_emails():
    """Standalone function to process and send due email tasks."""
    due_email_tasks = EmailTask.objects.filter(sent=False, time_to_send__lte=now())
    if due_email_tasks.exists():
        execute_email_tasks(due_email_tasks)
        print(f"Processed {due_email_tasks.count()} due email tasks.")
    else:
        print("No due email tasks to process.")
