from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from users.models import User, Support
from plans.models import Plan, Order, OrderItem
from payments.models import Payment

@login_required
@staff_member_required
def custom_admin_dashboard(request):
    stats = {
        "user_count": User.objects.count(),
        "service_count": Plan.objects.filter(is_active=True).count(),
        "order_count": OrderItem.objects.filter(quantity=1).count(),
        "ticket_count": Support.objects.filter(status="open").count(),
        "payment_count": Payment.objects.filter(status="success").count(),
    }
    return render(request, "dashboard/admin_dashboard.html", {"stats": stats})

@login_required
def dashboard_users(request):
    users = User.objects.all().order_by("-mobile")
    return render(request, "dashboard/users.html", {"users": users})

@login_required
def dashboard_plans(request):
    services = Plan.objects.all()
    return render(request, "dashboard/plan.html", {"services": services})

@login_required
def dashboard_orders(request):
    services = Order.objects.all()
    return render(request, "dashboard/order.html", {"services": services})

@login_required
def dashboard_tickets(request):
    tickets = Support.objects.all().order_by("-created_at")
    return render(request, "dashboard/ticket.html", {"tickets": tickets})

@login_required
def dashboard_payments(request):
    payments = Payment.objects.all().order_by("-created_at")
    return render(request, "dashboard/payments.html", {"payments": payments})
