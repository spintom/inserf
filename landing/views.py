from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.db import transaction
import json
from decimal import Decimal

from core.models import PurchaseOrder, Product, ProductVariant, Client, Cart, CartItem, OrderItem


from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm

def home(request):
    contact_success = False
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Try to send an email to site contact (ignore bots via honeypot)
            if not form.cleaned_data.get('hpot'):
                subject = "Nuevo contacto desde el sitio INSERF"
                message = form.cleaned_summary()
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or form.cleaned_data.get('email')
                recipient_list = [getattr(settings, 'CONTACT_EMAIL', 'contacto@inserf.cl')]
                try:
                    send_mail(subject, message, from_email, recipient_list, fail_silently=True)
                except Exception:
                    # Silently ignore any email errors to avoid breaking UX
                    pass
            contact_success = True
            form = ContactForm()  # reset form
    context = {
        'contact_form': form,
        'contact_success': contact_success,
    }
    return render(request, "landing/home.html", context)


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'admin':
                return '/admin-panel/'
            elif user.role == 'cliente':
                return '/my-orders/'
        return '/'


@login_required
def my_orders(request):
    if request.user.role != 'client':
        return redirect('/')
    orders = PurchaseOrder.objects.filter(client__user=request.user)
    return render(request, 'landing/my_orders.html', {'orders': orders})


@login_required
def catalog(request):
    # Get all active products with their variants
    products = Product.objects.filter(is_active=True).prefetch_related('variants')

    # Group products by category for better organization
    from collections import OrderedDict
    categories = {}
    for product in products:
        if product.category not in categories:
            categories[product.category] = []

        # Flags for template logic
        has_standard_variant = product.variants.filter(has_variants=False).exists()
        product.has_variants = product.variants.filter(has_variants=True).exists()
        product.has_standard_variant = has_standard_variant

        # Keep existing variants data (not strictly needed now that we render inline)
        product.all_variants_data = list(product.variants.values(
            'id', 'color', 'size', 'weight', 'is_luminous', 'unit_price', 'bulk_price', 'stock', 'has_variants', 'image_url'
        ))

        categories[product.category].append(product)

    # Sort categories and products alphabetically
    sorted_categories = OrderedDict()
    for cat in sorted(categories.keys(), key=lambda x: (x or '').lower()):
        sorted_categories[cat] = sorted(categories[cat], key=lambda p: (p.name or '').lower())

    # Get cart count for the user
    cart_count = 0
    if hasattr(request.user, 'client'):
        client = request.user.client
        cart = Cart.objects.filter(client=client).first()
        if cart:
            cart_count = cart.items.count()

    context = {
        'categories': sorted_categories,
        'products': products,
        'cart_count': cart_count,
    }

    return render(request, 'landing/catalog.html', context)


@login_required
def cart(request):
    if request.user.role != 'client':
        return redirect('/')
    
    # Get client's cart
    client = get_object_or_404(Client, user=request.user)
    cart = Cart.objects.filter(client=client).first()
    
    cart_items = []
    total = 0
    net_total = 0
    vat_total = 0
    
    if cart:
        # Get cart items with related objects
        cart_items = cart.items.select_related('variant', 'variant__product').all()
        
        # Calculate totals
        for item in cart_items:
            # Use the properties directly
            total += item.subtotal
            net_total += item.net_subtotal
            vat_total += item.vat_subtotal
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'net_total': net_total,
        'vat_total': vat_total,
        'cart_count': len(cart_items)
    }
    
    return render(request, 'landing/cart.html', context)


@login_required
def add_to_cart(request):
    if request.method != 'POST' or request.user.role != 'client':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        # Parse JSON data
        data = json.loads(request.body)
        variant_id = data.get('variant_id')
        quantity = int(data.get('quantity', 1))
        
        # Validate data
        if not variant_id or quantity < 1:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)
        
        # Get product variant
        variant = get_object_or_404(ProductVariant, id=variant_id)
        
        # Check stock
        if variant.stock < quantity:
            return JsonResponse({
                'success': False, 
                'error': f'Stock insuficiente. Solo hay {variant.stock} unidades disponibles.'
            }, status=400)
        
        # Get or create client's cart
        client = get_object_or_404(Client, user=request.user)
        cart, created = Cart.objects.get_or_create(client=client)
        
        # Check if item already exists in cart
        cart_item = CartItem.objects.filter(cart=cart, variant=variant).first()
        
        if cart_item:
            # Update quantity if item exists
            cart_item.quantity += quantity
            # Update variant details in case they've changed
            cart_item.variant_details = variant.get_variant_display()
            cart_item.save()
        else:
            # Create new cart item
            CartItem.objects.create(
                cart=cart,
                variant=variant,
                quantity=quantity,
                variant_details=variant.get_variant_display()
            )
        
        # Get updated cart count
        cart_count = cart.items.count()
        
        # Prepare response message based on variant type
        message = 'Producto agregado al carrito'
        if variant.has_variants:
            message = f'Producto con variante "{variant.get_variant_display()}" agregado al carrito'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_count': cart_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def update_cart_item(request):
    if request.method != 'POST' or request.user.role != 'client':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        # Parse JSON data
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        
        # Validate data
        if not item_id or quantity < 1:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)
        
        # Get cart item
        client = get_object_or_404(Client, user=request.user)
        cart = get_object_or_404(Cart, client=client)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        # Check stock
        if cart_item.variant.stock < quantity:
            return JsonResponse({
                'success': False, 
                'error': f'Stock insuficiente. Solo hay {cart_item.variant.stock} unidades disponibles.'
            }, status=400)
        
        # Update quantity
        cart_item.quantity = quantity
        cart_item.save()
        
        # Get updated cart count
        cart_count = cart.items.count()
        
        return JsonResponse({
            'success': True,
            'message': 'Carrito actualizado',
            'cart_count': cart_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def remove_cart_item(request):
    if request.method != 'POST' or request.user.role != 'client':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        # Parse JSON data
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        # Validate data
        if not item_id:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)
        
        # Get cart item
        client = get_object_or_404(Client, user=request.user)
        cart = get_object_or_404(Cart, client=client)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        # Delete cart item
        cart_item.delete()
        
        # Get updated cart count
        cart_count = cart.items.count()
        
        return JsonResponse({
            'success': True,
            'message': 'Producto eliminado del carrito',
            'cart_count': cart_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def checkout(request):
    if request.user.role != 'client':
        return redirect('/')
    
    # Get client's cart
    client = get_object_or_404(Client, user=request.user)
    cart = Cart.objects.filter(client=client).first()
    
    # If cart is empty, redirect to cart page
    if not cart or not cart.items.exists():
        return redirect('landing:cart')
    
    # Get cart items with related objects
    cart_items = cart.items.select_related('variant', 'variant__product').all()
    
    # Calculate totals
    total = 0
    net_total = 0
    vat_total = 0
    
    for item in cart_items:
        # Use the properties directly
        total += item.subtotal
        net_total += item.net_subtotal
        vat_total += item.vat_subtotal
    
    context = {
        'client': client,
        'cart_items': cart_items,
        'total': total,
        'net_total': net_total,
        'vat_total': vat_total,
        'cart_count': len(cart_items)
    }
    
    return render(request, 'landing/checkout.html', context)


@login_required
def process_checkout(request):
    if request.method != 'POST' or request.user.role != 'client':
        return redirect('landing:cart')
    
    # Get client's cart
    client = get_object_or_404(Client, user=request.user)
    cart = get_object_or_404(Cart, client=client)
    
    # If cart is empty, redirect to cart page
    if not cart.items.exists():
        return redirect('landing:cart')
    
    # Get form data
    company_name = request.POST.get('company_name')
    tax_id = request.POST.get('tax_id')
    address = request.POST.get('address')
    phone = request.POST.get('phone')
    email = request.POST.get('email')
    payment_method = request.POST.get('payment_method')
    notes = request.POST.get('notes', '')
    
    # Update client information if changed
    if (company_name != client.company_name or tax_id != client.tax_id or 
        address != client.address or phone != client.phone or email != client.email):
        client.company_name = company_name
        client.tax_id = tax_id
        client.address = address
        client.phone = phone
        client.email = email
        client.save()
    
    # Calculate totals
    cart_items = cart.items.select_related('variant').all()
    total = 0
    net_total = 0
    vat_total = 0
    
    for item in cart_items:
        # Use the properties directly
        total += item.subtotal
        net_total += item.net_subtotal
        vat_total += item.vat_subtotal
    
    # Create order with transaction to ensure data integrity
    with transaction.atomic():
        # Create purchase order
        order = PurchaseOrder.objects.create(
            client=client,
            status='pendiente',
            total_amount=total,
            net_total=net_total,
            vat_total=vat_total,
            notes=notes
        )
        
        # Create order items
        for cart_item in cart_items:
            # Calculate prices
            unit_price = cart_item.variant.unit_price
            net_unit_price = unit_price / Decimal('1.19')  # Assuming 19% VAT
            vat_amount = unit_price - net_unit_price
            subtotal = unit_price * cart_item.quantity
            net_subtotal = net_unit_price * cart_item.quantity
            vat_subtotal = vat_amount * cart_item.quantity
                
            OrderItem.objects.create(
                order=order,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                unit_price=unit_price,
                net_unit_price=net_unit_price,
                vat_amount=vat_amount,
                subtotal=subtotal,
                net_subtotal=net_subtotal,
                vat_subtotal=vat_subtotal,
                variant_details=cart_item.variant_details or cart_item.variant.get_variant_display()
            )
        
        # Clear cart
        cart.items.all().delete()
    
    # Redirect to confirmation page
    return redirect('landing:order_confirmation', order_id=order.id)


@login_required
def order_confirmation(request, order_id):
    if request.user.role != 'client':
        return redirect('/')
    
    # Get order
    order = get_object_or_404(PurchaseOrder, id=order_id, client__user=request.user)
    
    context = {
        'order': order
    }
    
    return render(request, 'landing/order_confirmation.html', context)
