from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.db.models import Sum
from stock_track.models import Product, ProductVariation, Inventory, InventoryLog, Batch
from profiles.models import Client
from django.utils import timezone


'''
I'll ask the free trial users owner about


1. Product removal from batch:
which batch to remove the product from, currently its removing from the oldest

'''

class Coupon(models.Model):
    company_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coupons",
        verbose_name="Company Owner",
    )
    code = models.CharField(max_length=50, unique=True, verbose_name="Coupon Code")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Discount Percentage")
    active = models.BooleanField(default=True, verbose_name="Active Status")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Expiry Date")

    def is_valid(self):
        return self.active and (self.expiry_date is None or self.expiry_date >= timezone.now().date())

    def __str__(self):
        return f"{self.code} - {self.discount_percentage}%"

class Sale(models.Model):
    company_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sales",
        verbose_name="Company Owner"
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="sales",
        verbose_name="Client"
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales",
        verbose_name="Applied Coupon"
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False, blank=True)
    sale_time = models.DateTimeField(auto_now_add=True, verbose_name="Sale Date & Time")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    def update_total_price(self):
        """
        Updates the total price of the sale based on its related sale items and applied coupon.
        """
        total = self.items.aggregate(total=Sum('total_price'))['total'] or 0
        if self.coupon and self.coupon.is_valid():
            discount = (self.coupon.discount_percentage / 100) * total
            total -= discount
        self.total_price = total
        self.save()

    def __str__(self):
        return f"Sale to {self.client.name} on {self.sale_time.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
        

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

class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Sale"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="sale_items",
        verbose_name="Product"
    )
    product_variation = models.ForeignKey(
        ProductVariation,
        on_delete=models.CASCADE,
        related_name="sale_items",
        verbose_name="Product Variation",
        null=True,
        blank=True,
        help_text="Leave empty if the product has no variation."
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    def save(self, *args, **kwargs):
        # Automatically fetch the unit price from the Product or ProductVariation model
        if not self.product_variation:
            if not self.unit_price:
                self.unit_price = self.product.price
        else:
            if not self.unit_price:
                self.unit_price = self.product_variation.price

        # Calculate total price based on quantity and unit price
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

        # Update the total price of the related sale
        self.sale.update_total_price()

    def __str__(self):
        return f"{self.product.name} ({self.product_variation.name if self.product_variation else 'No Variation'}) - Qty: {self.quantity}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sale', 'product', 'product_variation'], name='unique_sale_item')
        ]
        verbose_name = "Sale Item"
        verbose_name_plural = "Sale Items"

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
