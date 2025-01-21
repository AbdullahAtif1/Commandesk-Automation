from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from concurrent.futures import ThreadPoolExecutor

'''
I'll ask the free trial users owner about


1. Reorder Level:

Reason to Remove:
Not required if you're not automating stock reordering or alert systems.
Impact:
This simplifies stock management but requires manual oversight to avoid stockouts.

'''

class Warehouse(models.Model):
    company_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="warehouses",
        verbose_name="Owner"
    )
    name = models.CharField(max_length=150)
    address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    company_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="suppliers",
        verbose_name="Owner"
    )
    name = models.CharField(max_length=150)
    contact_details = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name


class Batch(models.Model):
    company_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="batches",
        verbose_name="Owner"
    )
    batch_number = models.CharField(max_length=50, unique=True)
    manufacture_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, blank=True, null=True, related_name="batches",
                                  help_text="Leave empty if there is no supplier and the product is your own.")

    def __str__(self):
        return f"Batch {self.batch_number}"
    
    def is_expired(self):
        """Returns True if the batch is expired, False otherwise."""
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False
    
    class Meta:
        verbose_name_plural = "Batches"


class Category(models.Model):
    company_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="Owner"
    )
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    company_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Owner"
    )
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    stock_alert_threshold = models.PositiveIntegerField(default=10)  # New field for inventory alerts
    batches = models.ManyToManyField(Batch, related_name="products", blank=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"


class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variations")
    name = models.CharField(max_length=100)  # e.g., "Small", "Large", "Red"
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_variations/', blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class Inventory(models.Model):
    company_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inventories",
        verbose_name="Owner"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory")
    product_variation = models.ForeignKey(
        ProductVariation, on_delete=models.CASCADE, related_name="inventory",
        null=True, blank=True, help_text="Leave empty if the product has no variation"
    )
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="inventory")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="inventory")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Changed to DecimalField
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product_variation', 'batch', 'warehouse')  # Prevent duplicate records per warehouse

    def __str__(self):
        return f"{self.product_variation.product.name} - Batch: {self.batch.batch_number} (Qty: {self.quantity})"

    class Meta:
        verbose_name_plural = "Inventories"


class InventoryLog(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="logs")
    change_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.inventory.product} - Change: {self.change_quantity}"



def send_email_notification(company_owner, email_subject, email_body):
    """
    Sends an email notification to the company owner.
    """
    send_mail(
        subject = email_subject,
        message = email_body,
        from_email = settings.EMAIL_HOST_USER,
        recipient_list = [company_owner.email],
        fail_silently = False,
    )

executor = ThreadPoolExecutor(max_workers=5)

def send_email_in_background(company_owner, email_subject, email_body):
    """
    Schedule the email notification to run in the background.
    """
    executor.submit(send_email_notification, company_owner, email_subject, email_body)

