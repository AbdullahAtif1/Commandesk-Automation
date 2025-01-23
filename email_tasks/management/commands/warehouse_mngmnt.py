from django.utils.timezone import now, timedelta
from django.db.models import Sum, F
from stock_track.models import Warehouse, Inventory, Batch, send_email_in_background

def warehouse_stock_overview(task=None):
    """
    Sends a single weekly summary notification for all warehouses, including:
    - Total inventory per warehouse
    - Low-stock items per warehouse
    - Expiring batches per warehouse
    """
    # Get today's date and calculate one week from now for expiring batches
    today = now().date()
    one_week_from_now = today + timedelta(days=7)

    # Initialize a list to store summaries for all warehouses
    warehouse_summaries = []

    # Iterate through all warehouses
    for warehouse in Warehouse.objects.all():
        warehouse_name = warehouse.name

        # 1. Total inventory in the warehouse
        total_inventory = Inventory.objects.filter(warehouse=warehouse).aggregate(
            total_quantity=Sum('quantity')
        )['total_quantity'] or 0

        # 2. Low-stock items (items below their stock_alert_threshold)
        low_stock_items = Inventory.objects.filter(
            warehouse=warehouse,
            quantity__lte=F('product__stock_alert_threshold')
        ).select_related('product')

        low_stock_summary = [
            f"{item.product.name} (Current: {item.quantity}, Threshold: {item.product.stock_alert_threshold})"
            for item in low_stock_items
        ]

        # 3. Expiring batches (batches expiring within the next 7 days)
        expiring_batches = Batch.objects.filter(
            expiry_date__gte=today,
            expiry_date__lte=one_week_from_now,
            inventory__warehouse=warehouse
        ).distinct()

        expiring_batches_summary = [
            f"{batch.batch_number} of {batch.inventory_set.first().product.name} (Expires: {batch.expiry_date})"
            for batch in expiring_batches
        ]

        # Compile the warehouse summary
        warehouse_summary = (
            f"Warehouse: {warehouse_name}\n"
            f"1. Total Inventory: {total_inventory} units\n"
            f"2. Low-Stock Items:\n"
            + ("\n".join(low_stock_summary) if low_stock_summary else "No low-stock items") + "\n"
            f"3. Expiring Batches:\n"
            + ("\n".join(expiring_batches_summary) if expiring_batches_summary else "No expiring batches") + "\n\n"
        )

        # Add the warehouse summary to the list
        warehouse_summaries.append(warehouse_summary)

    # Get the company owner (assuming all warehouses have the same owner)
    owner = Warehouse.objects.first().company_owner

    # Prepare the email content
    email_subject = "Weekly Stock Overview for All Warehouses"
    email_body = (
        f"Dear {owner.username},\n\n"
        f"Weekly Summary for All Warehouses:\n\n"
        + "\n".join(warehouse_summaries) +
        "Thank you."
    )

    # Send the email notification
    send_email_in_background(owner, email_subject, email_body)

    print("Warehouse stock overview notification sent successfully.")