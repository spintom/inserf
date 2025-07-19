from django.urls import path

from . import views

urlpatterns = [
    path('', views.admin_home, name='admin_home'),
    path("client/", views.list_clients, name="client_home"),
]
