from .models import Order
from django.utils import timezone
from datetime import timedelta

def get_or_create_open_order(user):
    now = timezone.now()
    one_day_ago = now - timedelta(days=1)

    # همه سفارش‌های draft کاربر که بیش از یک روز قدیمی هستند
    old_orders = Order.objects.filter(user=user, status='draft', created_at__lt=one_day_ago)
    old_orders.update(status='canceled')  # لغو خودکار

    # بررسی سفارش‌های draft معتبر (کمتر از یک روز)
    order = Order.objects.filter(user=user, status='draft', created_at__gte=one_day_ago).first()

    if order:
        return order

    # اگر سفارش معتبر نبود، ایجاد سفارش جدید
    return Order.objects.create(user=user, status='draft', total_price=0)