from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.db.models import Sum
from stock_track.models import Product, ProductVariation, Inventory, InventoryLog, Batch
from profiles.models import Client
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
import threading
from concurrent.futures import ThreadPoolExecutor
from django.core.mail import send_mail
import random

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


# EmailTask model logs tasks with metadata to manage and send emails.
class EmailTask(models.Model):
    EMAIL_TYPES = [
        ("thank_you", "Thank You Email"),
        ("feedback", "Feedback Email"),
        ("recommendation", "Recommendation Email"),
    ]
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='email_tasks',
        verbose_name="Sale"
    )
    email_type = models.CharField(
        max_length=50,
        choices=EMAIL_TYPES,
        verbose_name="Email Type"
    )
    time_to_send = models.DateTimeField(verbose_name="Time to Send")
    sent = models.BooleanField(default=False, verbose_name="Sent")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"{self.email_type} for Sale ID {self.sale.id} at {self.time_to_send}"

    class Meta:
        ordering = ['time_to_send']



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


def generate_product_recommendations(sale):
    """
    Generate product recommendations based on the categories of purchased products.
    """
    # Get all purchased products from the sale
    purchased_products = sale.items.all().values_list('product', flat=True)

    # Fetch the categories of the purchased products
    categories = Product.objects.filter(id__in=purchased_products).values_list('category', flat=True).distinct()

    # Initialize recommendations
    recommendations = []

    for category_id in categories:
        # Get all products in the category, excluding the purchased products
        category_products = Product.objects.filter(category_id=category_id).exclude(id__in=purchased_products)

        # Randomly sample up to 5 products from the category
        sampled_products = random.sample(list(category_products), min(len(category_products), 5))
        recommendations.extend(sampled_products)

    # Format the recommendations into a string
    recommendation_list = "\n".join([product.name for product in recommendations])

    # Return the recommendations or a default message
    return recommendation_list or "No recommendations available at this time."

# Function for directly sending in the email campaings after the sail to the company's client
def send_email_task(email_task):
    sale = email_task.sale
    company_owner = sale.company_owner
    recipient_email = sale.client.email  # Assuming the Client model has an email field.

    # Define email content
    email_subject = ""
    email_body = ""
    if email_task.email_type == "thank_you":
        email_subject = f"Thank You for Your Purchase, {sale.client.name}"
        email_body = f"Dear {sale.client.name},\n\nThank you for your recent purchase! We appreciate your business.\n\nBest Regards,\n{company_owner.company_name}"
    elif email_task.email_type == "feedback":
        email_subject = f"We'd Love Your Feedback, {sale.client.name}"
        email_body = f"Dear {sale.client.name},\n\nPlease share your feedback on your recent purchase to help us improve.\n\nBest Regards,\n{company_owner.company_name}"
    elif email_task.email_type == "recommendation":
        # Assuming you have a function to generate recommendations
        recommendations = generate_product_recommendations(sale)
        email_subject = "We Have Some Recommendations for You!"
        email_body = f"Dear {sale.client.name},\n\nBased on your previous purchases, you might like:\n{recommendations}\n\nBest Regards,\n{company_owner.company_name}"

    # Send email
    try:
        send_mail(
            subject=email_subject,
            message=email_body,
            from_email=company_owner.email,  # Sender's email
            recipient_list=[recipient_email],
            auth_user=company_owner.email,
            auth_password=company_owner.email_password,
            fail_silently=False,
        )
        email_task.sent = True  # Mark task as sent
        email_task.save()
    except Exception as e:
        print(f"Error sending email for task {email_task.id}: {e}")


executor = ThreadPoolExecutor(max_workers=5)

def execute_email_tasks(email_tasks):
    for email_task in email_tasks:
        executor.submit(send_email_task, email_task)
