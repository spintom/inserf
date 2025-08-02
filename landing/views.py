from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
import json

from core.models import PurchaseOrder, Product, ProductVariant, Client, Cart, CartItem


def home(request):
    return render(request, "landing/home.html")


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
    categories = {}
    for product in products:
        if product.category not in categories:
            categories[product.category] = []
        categories[product.category].append(product)
    
    # Get cart count for the user
    cart_count = 0
    if hasattr(request.user, 'client'):
        client = request.user.client
        cart = Cart.objects.filter(client=client).first()
        if cart:
            cart_count = cart.items.count()
    
    context = {
        'categories': categories,
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
    
    if cart:
        # Get cart items with related objects
        cart_items = cart.items.select_related('variant', 'variant__product').all()
        
        # Calculate total
        for item in cart_items:
            item.subtotal = item.variant.unit_price * item.quantity
            total += item.subtotal
    
    context = {
        'cart_items': cart_items,
        'total': total,
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
            cart_item.save()
        else:
            # Create new cart item
            CartItem.objects.create(
                cart=cart,
                variant=variant,
                quantity=quantity
            )
        
        # Get updated cart count
        cart_count = cart.items.count()
        
        return JsonResponse({
            'success': True,
            'message': 'Producto agregado al carrito',
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
