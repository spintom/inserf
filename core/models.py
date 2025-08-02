from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client', null=True, blank=True)
    company_name = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    email = models.EmailField()

    def __str__(self):
        return self.company_name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.CharField(max_length=50, blank=True)
    weight = models.FloatField(null=True, blank=True)
    size = models.CharField(max_length=50, blank=True)
    is_luminous = models.BooleanField(default=False)
    stock = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    bulk_price = models.DecimalField(max_digits=10, decimal_places=2)
    has_variants = models.BooleanField(default=True)

    def __str__(self):
        if not self.has_variants:
            return f"{self.product.name}"
        return f"{self.product.name} - {self.color}/{self.size}"
        
    def get_variant_display(self):
        if not self.has_variants:
            return "Producto sin variantes"
        
        variant_parts = []
        if self.color:
            variant_parts.append(f"Color: {self.color}")
        if self.size:
            variant_parts.append(f"Tamaño: {self.size}")
        if self.weight:
            variant_parts.append(f"Peso: {self.weight}g")
        if self.is_luminous:
            variant_parts.append("Luminoso")
            
        return ", ".join(variant_parts) if variant_parts else "Estándar"

class Cart(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart #{self.id} - {self.client.company_name}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField()
    variant_details = models.TextField(blank=True)  # Store variant details as text
    
    def save(self, *args, **kwargs):
        # Store variant details when saving the cart item
        if not self.variant_details and self.variant:
            self.variant_details = self.variant.get_variant_display()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.variant}"
        
    @property
    def subtotal(self):
        return self.variant.unit_price * self.quantity

class PurchaseOrder(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='purchase_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.client.company_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    variant_details = models.TextField(blank=True)  # Store variant details as text
    
    def save(self, *args, **kwargs):
        # Store variant details when saving the order item
        if not self.variant_details and self.variant:
            self.variant_details = self.variant.get_variant_display()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.variant} for Order #{self.order.id}"
