from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *
from django.utils.timezone import now
from datetime import timedelta


# Post Sale save signal to automatically create email sending tasks.
@receiver(post_save, sender=Sale)
def create_email_tasks(sender, instance, created, **kwargs):
    if created:
        now_time = now()
        EmailTask.objects.bulk_create([
            EmailTask(
                sale=instance,
                email_type="thank_you",
                time_to_send=now_time,
            ),
            EmailTask(
                sale=instance,
                email_type="feedback",
                time_to_send=now_time + timedelta(days=7),
            ),
            EmailTask(
                sale=instance,
                email_type="recommendation",
                time_to_send=now_time + timedelta(days=30),
            ),
        ])


@receiver(post_save, sender=Sale)
def update_client_total_spent_on_save(sender, instance, **kwargs):
    """
    Update the client's total spent field when a sale is created or updated.
    """
    client = instance.client
    total_spent = client.sales.aggregate(total=Sum('total_price'))['total'] or 0
    client.total_spent = total_spent
    client.save()


@receiver(post_delete, sender=Sale)
def update_client_total_spent_on_delete(sender, instance, **kwargs):
    """
    Update the client's total spent field when a sale is deleted.
    """
    client = instance.client
    total_spent = client.sales.aggregate(total=Sum('total_price'))['total'] or 0
    client.total_spent = total_spent
    client.save()


# Signal to update inventory and batch when a sale is made
@receiver(post_save, sender=SaleItem)
def update_inventory_and_batch(sender, instance, created, **kwargs):
    if created:
        try:
            # Update Inventory
            inventory = Inventory.objects.filter(
                product=instance.product,
                product_variation=instance.product_variation,
                warehouse=instance.sale.company_owner
            ).first()

            if inventory:
                if inventory.quantity >= instance.quantity:
                    inventory.quantity -= instance.quantity
                    inventory.save()

                    # Log inventory change
                    InventoryLog.objects.create(
                        inventory=inventory,
                        change_quantity=-instance.quantity,
                        reason=f"Sale to client {instance.sale.client.name}"
                    )
                else:
                    raise ValueError("Insufficient inventory to complete the sale")

            # Update the Batch directly
            batch = Batch.objects.filter(products=instance.product).order_by('manufacture_date').first()
            if batch:
                total_quantity_in_batch = Inventory.objects.filter(batch=batch).aggregate(total=Sum('quantity'))['total']
                if total_quantity_in_batch is not None and total_quantity_in_batch <= 0:
                    batch.products.remove(instance.product)
        except Exception as e:
            # Error Handling
            print(f"Error updating inventory and batch: {e}")
