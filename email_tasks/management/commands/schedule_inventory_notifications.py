from stock_track.models import Inventory, InventoryLog, send_email_in_background
from django.utils.timezone import now, timedelta




def inventory_management_notifications(task=None):
    """
    Function to send inventory-related email notifications.
    This function handles the following notifications:
    - New Inventory Added
    - Inventory Depleted from a Batch
    - Inventory Transfer Alert
    - Inventory Log Change
    """
    # 1. New Inventory Added
    # Assuming new inventory is added within the last minute (adjust as needed)
    new_inventory = Inventory.objects.filter(added_at__gte=now() - timedelta(minutes=1))
    for inventory in new_inventory:
        owner = inventory.company_owner
        product_name = inventory.product.name
        batch_number = inventory.batch.batch_number
        warehouse_name = inventory.warehouse.name
        email_subject = f"New Inventory Added: {product_name}"
        email_body = (
            f"Dear {owner.username},\n\n"
            f"New batch {batch_number} of product {product_name} has been added to {warehouse_name}.\n\n"
            "Thank you."
        )
        send_email_in_background(owner, email_subject, email_body)

    # 2. Inventory Depleted from a Batch
    depleted_inventory = Inventory.objects.filter(quantity=0)
    for inventory in depleted_inventory:
        owner = inventory.company_owner
        product_name = inventory.product.name
        batch_number = inventory.batch.batch_number
        warehouse_name = inventory.warehouse.name
        email_subject = f"Inventory Depleted: {product_name}"
        email_body = (
            f"Dear {owner.username},\n\n"
            f"Batch {batch_number} of product {product_name} in {warehouse_name} has been fully used.\n\n"
            "Thank you."
        )
        send_email_in_background(owner, email_subject, email_body)

    # 3. Inventory Transfer Alert
    # Assuming you have a way to track transfers (e.g., a separate model or log)
    # For simplicity, let's assume transfers are logged in InventoryLog with a specific reason
    transfer_logs = InventoryLog.objects.filter(reason__icontains="transferred")
    for log in transfer_logs:
        owner = log.inventory.company_owner
        product_name = log.inventory.product.name
        change_quantity = log.change_quantity
        warehouse_from = log.inventory.warehouse.name
        warehouse_to = log.reason.split("to")[-1].strip()  # Extract destination warehouse from reason
        email_subject = f"Inventory Transfer Alert: {product_name}"
        email_body = (
            f"Dear {owner.username},\n\n"
            f"{change_quantity} units of {product_name} have been transferred from {warehouse_from} to {warehouse_to}.\n\n"
            "Thank you."
        )
        send_email_in_background(owner, email_subject, email_body)

    # 4. Inventory Log Change
    # Notify for any manual changes logged in InventoryLog
    recent_logs = InventoryLog.objects.filter(created_at__gte=now() - timedelta(minutes=1))
    for log in recent_logs:
        owner = log.inventory.company_owner
        product_name = log.inventory.product.name
        change_quantity = log.change_quantity
        warehouse_name = log.inventory.warehouse.name
        reason = log.reason or "No reason provided"
        email_subject = f"Inventory Log Change: {product_name}"
        email_body = (
            f"Dear {owner.username},\n\n"
            f"{change_quantity} units have been added/removed from {product_name} in {warehouse_name}.\n"
            f"Reason: {reason}\n\n"
            "Thank you."
        )
        send_email_in_background(owner, email_subject, email_body)

    print("Inventory management notifications sent successfully.")