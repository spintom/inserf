from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, home, my_orders

app_name = "landing"

urlpatterns = [
    path("", home, name="home"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("my-orders/", my_orders, name="my_orders"),
]
