import requests
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Payment, Order

# from .utils import notify_admin_new_order

ZIBAL_MERCHANT_ID = settings.ZIBAL_MERCHANT_ID
ZIBAL_REQUEST_URL = "https://gateway.zibal.ir/v1/request"
ZIBAL_VERIFY_URL = "https://gateway.zibal.ir/v1/verify"
ZIBAL_STARTPAY_URL = "https://gateway.zibal.ir/start/{trackId}"


@login_required
def start_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    amount_rial = int(order.total_price * 10)  # تبدیل تومان به ریال

    if order.status not in ["submitted", "draft"]:
        return HttpResponse("این سفارش قابل پرداخت نیست")

    # amount = int(order.total_price)
    # print(amount)

    data = {
        "merchant": ZIBAL_MERCHANT_ID,
        "amount": amount_rial,
        "callbackUrl": request.build_absolute_uri(f"/payments/verify/{order.id}/"),
        "description": f"پرداخت سفارش {order.id}",
    }
    print(data)
    response = requests.post(ZIBAL_REQUEST_URL, json=data)
    try:
        response_data = response.json()
    except Exception:
        return HttpResponse("خطا در ارتباط با درگاه زیبال")

    if response_data.get("result") == 100:
        track_id = response_data["trackId"]

        Payment.objects.create(
            order=order,
            user=request.user,
            amount=order.total_price,
            description=f"پرداخت سفارش {order.id}",
            ref_id=track_id,  # ذخیره موقت
            status="pending",
        )
        print(track_id)
        return redirect(ZIBAL_STARTPAY_URL.format(trackId=track_id))
    else:
        return HttpResponse(f"خطا در ایجاد تراکنش: {response_data}")


@login_required
def verify_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment = order.payments.last()

    track_id = request.GET.get("trackId")

    if not payment or not track_id:
        return HttpResponse("پرداخت پیدا نشد")

    # فقط با verify از زیبال استعلام کن
    data = {
        "merchant": ZIBAL_MERCHANT_ID,
        "trackId": track_id,
    }

    response = requests.post(ZIBAL_VERIFY_URL, json=data)
    response_data = response.json()

    if response_data.get("result") == 100:  # پرداخت موفق
        payment.status = "success"
        payment.ref_id = response_data.get("refNumber")
        payment.save()

        order.status = "paid"
        order.save()

        notify_admin_new_order(order)
        return render(request, "payment_success.html", {"payment": payment, "order": order})
    else:
        payment.status = "canceled"
        payment.save()
        order.status = "canceled"
        order.save()
        return render(request, "payment_failed.html", {"payment": payment, "order": order})


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .utils import notify_admin_new_order, send_template_sms


@csrf_exempt
def test_sms(request):
    """
    سه حالت:
    - ?use_order=1  -> از آخرین Order در DB استفاده می‌کند (اگر موجود باشد)
    - در غیر این صورت، از پارامترهای mobile, price, items استفاده می‌کند
    مثال:
    /test-sms/?mobile=09012345678&price=120000&items=PlanA×1
    """
    # اگر خواستی با سفارش واقعی تست کنی:
    if request.GET.get("use_order") == "1":
        order = Order.objects.last()
        if not order:
            return JsonResponse({"error": "هیچ سفارشی وجود ندارد"})
        # اگر توی notify_admin_new_order از template استفاده می‌کنی، می‌تونی:
        resp = notify_admin_new_order(order)
        return JsonResponse(resp)

    # حالت بدون سفارش: پارامترها از GET می آیند یا مقدار پیش‌فرض
    mobile = request.GET.get("mobile", "09052427494")  # شماره ادمین یا شماره تستی
    price = request.GET.get("price", "10000")
    items = request.GET.get("items", "محصول تست × 1")

    template_id = getattr(settings, "TEMPLATE_ID", None)
    if not template_id:
        return JsonResponse({"error": "SMSIR_ORDER_TEMPLATE_ID در settings تعریف نشده است"}, status=500)

    # نام پارامترها باید دقیقا مثل چیزی باشه که توی پنل template گذاشتی
    params = [
        {"name": "ORDER.USER.MOBILE", "value": mobile},
        {"name": "ORDER.TOTAL_PRICE", "value": str(price)},
        {"name": "ITEMS", "value": items},
    ]

    resp = send_template_sms(mobile, template_id, params)
    return JsonResponse(resp)


# ===========================
# تراکنش‌های اخیر
# ===========================
@login_required
def transactions(request):
    transaction = Payment.objects.filter(user=request.user).order_by("-created_at")[:5]
    print(transaction)
    return render(request, "transactions.html", {"transactions": transaction})
