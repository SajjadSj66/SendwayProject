import os
import django

# مسیر settings پروژه
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SendWayProject.settings")
django.setup()

import random
from plans.models import OrderItem, Plan
from payments.models import Order, Payment
# from users.models import User
from payments.utils import notify_admin_new_order
from django.contrib.auth import get_user_model


User = get_user_model()

def test_payment_flow():
    # 1️⃣ انتخاب کاربر و پلن تستی
    user = User.objects.first()
    if not user:
        print("هیچ یوزری پیدا نشد!")
        return

    plan = Plan.objects.first()
    if not plan:
        print("هیچ پلنی پیدا نشد!")
        return

    # 2️⃣ ایجاد سفارش
    order = Order.objects.create(user=user, status="draft")
    OrderItem.objects.create(order=order, plan=plan, quantity=2)
    print(f"سفارش ایجاد شد: ID={order.id}, مبلغ کل={order.total_price}")

    # 3️⃣ شبیه‌سازی شروع پرداخت
    track_id = str(random.randint(1000000, 9999999))
    payment = Payment.objects.create(
        order=order,
        user=user,
        amount=order.total_price,
        description=f"پرداخت سفارش {order.id}",
        ref_id=track_id,
        status="pending",
    )
    print(f"پرداخت ایجاد شد: trackId={track_id}, وضعیت={payment.status}")

    # 4️⃣ شبیه‌سازی تایید پرداخت موفق
    success = True  # True برای موفق، False برای ناموفق

    if success:
        payment.status = "success"
        payment.ref_id = str(random.randint(10000000, 99999999))  # شماره تراکنش واقعی شبیه‌سازی
        payment.save()

        # وضعیت سفارش مستقیم به paid
        order.status = "paid"
        order.save()

        print(f"پرداخت موفق! وضعیت سفارش: {order.status}, وضعیت پرداخت: {payment.status}")

        # 5️⃣ ارسال پیامک به ادمین (در صورت فعال بودن API)
        try:
            sms_response = notify_admin_new_order(order)
            print("پیامک ادمین ارسال شد:", sms_response)
        except Exception as e:
            print("خطا در ارسال پیامک:", e)

    else:
        payment.status = "failed"
        payment.save()
        order.status = "canceled"
        order.save()
        print(f"پرداخت ناموفق! وضعیت سفارش: {order.status}, وضعیت پرداخت: {payment.status}")


# اجرا
if __name__ == "__main__":
    test_payment_flow()