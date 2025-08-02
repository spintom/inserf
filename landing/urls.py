from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    CustomLoginView, home, my_orders, catalog,
    cart, add_to_cart, update_cart_item, remove_cart_item
)

app_name = "landing"

urlpatterns = [
    path("", home, name="home"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("my-orders/", my_orders, name="my_orders"),
    path("catalog/", catalog, name="catalog"),
    
    # Cart URLs
    path("cart/", cart, name="cart"),
    path("cart/add/", add_to_cart, name="add_to_cart"),
    path("cart/update/", update_cart_item, name="update_cart_item"),
    path("cart/remove/", remove_cart_item, name="remove_cart_item"),
]
