from stock_track.models import Batch, Inventory, send_email_in_background
from django.utils.timezone import now, timedelta
from django.db.models import F


def expiration_stock_alerts(task=None):
    """
    Function to send inventory-related email notifications.
    This function handles the following notifications:
    - Batch Expiration Reminder
    - Expired Batch Alert
    - Low Stock Alert
    - No Stock Notification
    """
    # Get today's date and calculate one week from now
    today = now().date()
    one_week_from_now = today + timedelta(days=7)

    # 1. Batch Expiration Reminder
    expiring_batches = Batch.objects.filter(expiry_date=one_week_from_now)
    for batch in expiring_batches:
        owner = batch.company_owner
        email_subject = f"Batch Expiration Reminder: Batch {batch.batch_number}"
        email_body = (
            f"Dear {owner.username},\n\n"
            f"Batch {batch.batch_number} of product(s) in your inventory will expire in 7 days.\n\n"
            "Thank you."
        )
        send_email_in_background(owner, email_subject, email_body)

    # 2. Expired Batch Alert
    expired_batches = Batch.objects.filter(expiry_date__lt=today)
    for batch in expired_batches:
        owner = batch.company_owner
        email_subject = f"Expired Batch Alert: Batch {batch.batch_number}"
        email_body = (
            f"Dear {owner.username},\n\n"
            f"Batch {batch.batch_number} of product(s) in your inventory has expired.\n\n"
            "Please take necessary action.\n\nThank you."
        )
        send_email_in_background(owner, email_subject, email_body)

    # 3. Low Stock Alert
    low_stock_inventory = Inventory.objects.filter(quantity__lt=F('product__stock_alert_threshold'))
    for inventory in low_stock_inventory:
        owner = inventory.company_owner
        product_name = inventory.product.name
        warehouse_name = inventory.warehouse.name
        email_subject = f"Low Stock Alert: {product_name}"
        email_body = (
            f"Dear {owner.username},\n\n"
            f"The stock for {product_name} in Warehouse {warehouse_name} has fallen below the threshold.\n\n"
            "Thank you."
        )
        send_email_in_background(owner, email_subject, email_body)

    # 4. No Stock Notification
    zero_stock_inventory = Inventory.objects.filter(quantity=0)
    for inventory in zero_stock_inventory:
        owner = inventory.company_owner
        product_name = inventory.product.name
        warehouse_name = inventory.warehouse.name
        email_subject = f"No Stock Notification: {product_name}"
        email_body = (
            f"Dear {owner.username},\n\n"
            f"The stock for {product_name} in Warehouse {warehouse_name} is completely out.\n\n"
            "Thank you."
        )
        send_email_in_background(owner, email_subject, email_body)

    print("Inventory notifications sent successfully.")





