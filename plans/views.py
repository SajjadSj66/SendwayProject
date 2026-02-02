from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Plan, Order, OrderItem
from .forms import OrderForm
from .services import get_or_create_open_order
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import logging

logger = logging.getLogger(__name__)


# ------------------  فرم سفارش  ------------------
# def checkout_view(request):
#     if request.method == "POST":
#         form = CheckoutForm(request.POST)
#         if form.is_valid():
#             form.save()   # ذخیره در دیتابیس
#             return redirect("success_page")  # به صفحه موفقیت برو
#     else:
#         form = CheckoutForm()
#
#     return render(request, "sabtsefaresh.html", {"form": form})


# ------------------  نمایش پلن‌ها (صفحه packages) ------------------
@login_required
def plan_list(request):
    # اینجا می‌تونی براساس دسته‌بندی یا هر فیلدی که داری گروه بسازی
    groups = [
        {
            "slug": "کاربران تصادفی",
            "slug_en": "random_users",
            "title": "کاربران تصادفی",
            "plans": Plan.objects.filter(category="کاربران تصادفی")
        },
        {
            "slug": "لایک کننده",
            "slug_en": "likers",
            "title": "لایک کننده",
            "plans": Plan.objects.filter(category="لایک کننده")
        },
        {
            "slug": "کامنت‌گذار",
            "slug_en": "commenters",
            "title": "کامنت‌گذار",
            "plans": Plan.objects.filter(category="کامنت‌گذار")
        },
        {
            "slug": "هشتگ",
            "slug_en": "hashtag",
            "title": "هشتگ",
            "plans": Plan.objects.filter(category="هشتگ")
        },
        {
            "slug": "لوکیشن",
            "slug_en": "location",
            "title": "لوکیشن",
            "plans": Plan.objects.filter(category="لوکیشن")
        },
        {
            "slug": "اکسپلور",
            "slug_en": "explore",
            "title": "اکسپلور",
            "plans": Plan.objects.filter(category="اکسپلور")
        },
    ]
    return render(request, "packages.html", {"groups": groups})


# ------------------  افزودن پلن به سبد خرید ------------------
# @login_required
# def add_to_cart(request, plan_id):
#     plan = get_object_or_404(Plan, id=plan_id, is_active=True)
#
#     cart = request.session.get('cart', {})
#
#     if str(plan.id) in cart:
#         cart[str(plan.id)]['quantity'] += 1
#     else:
#         cart[str(plan.id)] = {
#             'title': plan.title,
#             'price': float(plan.price),
#             'quantity': 1,
#         }
#
#     request.session['cart'] = cart
#     messages.success(request, f"پلن {plan.title} به سبد خرید اضافه شد.")
#     return redirect('checkout')


# @login_required
# @require_POST
# def merge_cart(request):
#     try:
#         payload = json.loads(request.body.decode('utf-8') or '{}')
#     except ValueError:
#         return HttpResponseBadRequest('invalid json')
#
#     cart = payload.get('cart', {})
#     if not isinstance(cart, dict):
#         return HttpResponseBadRequest('cart must be dict')
#
#     order = get_or_create_open_order(request.user)
#
#     with transaction.atomic():
#         # همگام‌سازی: برای هر آیتم، quantity را ست کن؛ اگر 0 -> پاک کن
#         for plan_id_str, qty in cart.items():
#             try:
#                 plan_id = int(plan_id_str)
#                 qty = int(qty)
#             except Exception:
#                 continue
#
#             try:
#                 plan = Plan.objects.get(id=plan_id, is_active=True)
#             except Plan.DoesNotExist:
#                 continue
#
#             if qty <= 0:
#                 OrderItem.objects.filter(order=order, plan=plan).delete()
#                 continue
#
#             item, created = OrderItem.objects.get_or_create(order=order, plan=plan,
#                                                             defaults={'quantity': 0, 'total_price': 0})
#             item.quantity = qty
#             # توجه: با توجه به مدل تو، total_price صحیح می‌شود در save
#             item.total_price = plan.price * qty
#             item.save()
#
#         # حذف آیتم‌هایی که دیگر در cart نیستند
#         # انتخابی: می‌توانی این کار را انجام دهی یا نه؛ در اینجا نگه نداشتم تا فقط آیتم‌های ارسال‌شده را آپدیت کنم.
#         order.update_total_price()
#
#     return JsonResponse({'status': 'ok', 'order_id': order.id, 'total_price': str(order.total_price)})


# ------------------  ویو برای اضافه‌کردن پلن به سفارش ------------------
@login_required
def add_to_order(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id, is_active=True)
    order = get_or_create_open_order(request.user)

    item, created = OrderItem.objects.get_or_create(
        order=order,
        plan=plan,
        defaults={'quantity': 0, 'total_price': 0}
    )
    item.quantity += 1
    item.total_price = item.plan.price * item.quantity
    item.save()
    order.update_total_price()

    return redirect('checkout')


# ------------------  صفحه checkout (فرم + سبد خرید) ------------------
@login_required
def checkout(request):
    order = get_or_create_open_order(request.user)

    if request.method == "POST":
        form = OrderForm(request.POST, user=request.user, instance=order)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.phone = request.user.mobile  # شماره موبایل از مدل User میاد
            order.status = 'submitted'
            order.save()
            print("Order Status updated.")
            order.update_total_price()
            messages.success(request, "سفارش شما ثبت شد. در حال انتقال به درگاه پرداخت هستید.")

            # اطمینان از پر بودن order.id
            if order.items.count() == 0:
                form.add_error(None, "سبد خرید شما خالی است و نمی‌توانید پرداخت انجام دهید.")
            else:
                form.save()
                return redirect('start_payment', order_id=order.id)
    else:
        form = OrderForm(user=request.user, instance=order)
    # بروزرسانی جمع کل قبل از نمایش
    order.update_total_price()

    return render(request, 'sabtsefaresh.html', {
        'form': form,
        'order': order,
        'total_price': order.total_price,
    })


# ------------------  افزایش/کاهش تعداد آیتم‌ها ------------------
@login_required
def update_item_quantity(request, item_id, action):
    item = get_object_or_404(OrderItem, id=item_id)
    if action == "increase":
        item.quantity += 1
    elif action == "decrease" and item.quantity > 1:
        item.quantity -= 1

        # بروزرسانی total_price ردیف
    item.total_price = item.plan.price * item.quantity
    item.save()

    # بروزرسانی جمع کل سفارش
    item.order.update_total_price()

    return JsonResponse({
        "quantity": item.quantity,
        "row_total": item.total_price,
        "order_total": item.order.total_price,
    })


@require_POST
@login_required
def remove_item(request, item_id):
    print("yeaah")
    logger.info("remove_item called: user=%s item_id=%s", request.user, item_id)
    # فقط آیتمی که به این کاربر تعلق داره قبول کن (برای امنیت)
    item = OrderItem.objects.filter(id=item_id, order__user=request.user).select_related('order').first()
    print(item)
    if not item:
        logger.info("remove_item: item not found or not belongs to user: %s", item_id)
        return JsonResponse({'error': 'not_found'}, status=404)

    order = item.order
    logger.info("remove_item: deleting item %s from order %s", item.id, order.id)
    item.delete()

    # اگر بعد از حذف، آیتمی داخل order نماند -> حذف کل سفارش
    if not order.items.exists():
        logger.info("remove_item: order %s empty -> deleting order", order.id)
        order.delete()
        return JsonResponse({'deleted': True, 'order_total': 0})
    print("ok")

    # وگرنه جمع کل را بروزرسانی و بازگردان
    order.update_total_price()
    print("ok2")
    logger.info("remove_item: new order total = %s", order.total_price)
    # برای ایمن بودن JSON، می‌تونیم عدد رو به int یا str تبدیل کنیم
    return JsonResponse({'deleted': True, 'order_total': int(order.total_price)})


# ------------------  لیست سفارش‌های کاربر ------------------
@login_required
def order_list(request):
    # همه سفارش‌های کاربر (به همراه آیتم‌ها)
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items__plan")  # برای کاهش query
        .order_by("-created_at")
    )

    return render(request, "transactions.html", {"orders": orders})
