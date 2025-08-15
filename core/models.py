from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal

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
    image_url = models.URLField(blank=True)

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
    def net_price(self):
        """Returns the unit price without VAT"""
        return self.variant.unit_price / Decimal('1.19')  # Assuming 19% VAT
    
    @property
    def vat_amount(self):
        """Returns the VAT amount for a single unit"""
        return self.variant.unit_price - self.net_price
    
    @property
    def net_subtotal(self):
        """Returns the subtotal without VAT"""
        return self.net_price * self.quantity
    
    @property
    def vat_subtotal(self):
        """Returns the VAT amount for the subtotal"""
        return self.vat_amount * self.quantity
        
    @property
    def subtotal(self):
        """Returns the subtotal with VAT included"""
        return self.variant.unit_price * self.quantity

class PurchaseOrder(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='purchase_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)  # Total with VAT
    net_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Total without VAT
    vat_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # VAT amount
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.client.company_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price with VAT
    net_unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Price without VAT
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # VAT amount per unit
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)  # Subtotal with VAT
    net_subtotal = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Subtotal without VAT
    vat_subtotal = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # VAT amount for subtotal
    variant_details = models.TextField(blank=True)  # Store variant details as text
    
    def save(self, *args, **kwargs):
        # Calculate prices if not provided
        if not self.net_unit_price:
            self.net_unit_price = self.unit_price / Decimal('1.19')  # Assuming 19% VAT
        
        if not self.vat_amount:
            self.vat_amount = self.unit_price - self.net_unit_price
            
        if not self.net_subtotal:
            self.net_subtotal = self.net_unit_price * self.quantity
            
        if not self.vat_subtotal:
            self.vat_subtotal = self.vat_amount * self.quantity
            
        if not self.subtotal:
            self.subtotal = self.unit_price * self.quantity
            
        # Store variant details when saving the order item
        if not self.variant_details and self.variant:
            self.variant_details = self.variant.get_variant_display()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.variant} for Order #{self.order.id}"
