from django.urls import path
from . import views

urlpatterns = [
    path("", views.custom_admin_dashboard, name="dashboard_home"),
    path("users/", views.dashboard_users, name="dashboard_users"),
    path("plans/", views.dashboard_plans, name="dashboard_plans"),
    path("orders/", views.dashboard_orders, name="dashboard_orders"),
    path("tickets/", views.dashboard_tickets, name="dashboard_tickets"),
    path("payments/", views.dashboard_payments, name="dashboard_payments"),
]
