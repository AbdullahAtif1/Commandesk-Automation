from stock_track.models import Inventory, send_email_in_background
from django.db.models import F



def supplier_batch_delivery_reminder(task=None):
    """
    Notify the company_owner when a batch's stock level falls below the product's stock_alert_threshold,
    prompting them to contact the supplier for replenishment.
    """
    # Find batches with stock levels below the product's stock_alert_threshold
    low_stock_batches = Inventory.objects.filter(quantity__lte=F('product__stock_alert_threshold'))

    for inventory in low_stock_batches:
        owner = inventory.company_owner
        product_name = inventory.product.name
        batch_number = inventory.batch.batch_number
        supplier = inventory.batch.supplier
        stock_alert_threshold = inventory.product.stock_alert_threshold

        if supplier:  # Ensure the batch has a supplier
            email_subject = f"Supplier Batch Delivery Reminder: {product_name}"
            email_body = (
                f"Dear {owner.username},\n\n"
                f"The stock level for {product_name} (Batch {batch_number}) has fallen below the alert threshold of {stock_alert_threshold}. "
                f"Please contact {supplier.name} for replenishment.\n\n"
                f"Supplier Contact Details:\n"
                f"Email: {supplier.email}\n"
                f"Phone: {supplier.contact_details}\n\n"
                "Thank you."
            )
            send_email_in_background(owner, email_subject, email_body)

    print("Supplier batch delivery reminders sent successfully.")