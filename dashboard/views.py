from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpResponseForbidden
from django.shortcuts import render
from core.models import PurchaseOrder, ProductVariant, Client


def is_admin(user):
    return user.is_authenticated and user.role == "admin"


@login_required
def admin_home(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Acceso restringido a administradores.")

    total_orders = PurchaseOrder.objects.count()
    total_stock = ProductVariant.objects.aggregate(total=Sum("stock"))["total"] or 0
    total_clients = Client.objects.count()

    # Órdenes por estado
    orders_by_status = PurchaseOrder.objects.values("status").annotate(count=Count("id"))

    # Stock por categoría de productos
    stock_by_category = (
        ProductVariant.objects
        .select_related("product")
        .values("product__category")
        .annotate(total_stock=Sum("stock"))
    )

    context = {
        "total_orders": total_orders,
        "total_products": total_stock,
        "total_clients": total_clients,
        "orders_by_status": orders_by_status,
        "stock_by_category": stock_by_category,
    }
    return render(request, "dashboard/dashboard_home.html", context)


@login_required
def list_clients(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Acceso restringido a administradores.")

    clients = Client.objects.select_related("user").all()
    return render(request, "dashboard/client/admin_clients.html", {"clients": clients})
