from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.shortcuts import render

from core.models import PurchaseOrder, Product, ProductVariant


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
    
    context = {
        'categories': categories,
        'products': products,
    }
    
    return render(request, 'landing/catalog.html', context)
