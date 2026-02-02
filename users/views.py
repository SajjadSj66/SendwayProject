from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from payments.models import Payment
from .forms import MobileForm, OTPVerificationForm, SupportForm
from .models import *
from plans.models import *
from .utils import *
import random
import logging
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.urls import reverse


# Create your views here.
def index(request):
    return render(request, 'index.html')


logger = logging.getLogger(__name__)


@never_cache
def register_view(request):
    # ✅ اگر کاربر لاگین هست، نذار برگرده به صفحه ثبت‌نام
    if request.user.is_authenticated:
        return redirect("packages")

    pending_user_id = request.session.get("pending_user_id")

    # --- Step 2: OTP ---
    if pending_user_id:
        user = User.objects.filter(id=pending_user_id).first()
        if not user:
            request.session.pop("pending_user_id", None)
            return render(request, "register.html", {"form": MobileForm(), "step": "mobile"})

        latest_otp = PhoneOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()

        if not latest_otp or latest_otp.is_expired():
            request.session.pop("pending_user_id", None)
            return render(request, "register.html", {"form": MobileForm(), "step": "mobile"})

        cooldown_seconds = int(
            (latest_otp.created_at + timedelta(minutes=2) - timezone.now()).total_seconds()
        )
        cooldown_seconds = max(0, cooldown_seconds)

        if request.method == "POST":
            # --- Resend OTP ---
            if "resend" in request.POST or "resend_otp" in request.POST:
                latest = PhoneOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()
                if latest and not latest.is_expired():
                    remaining = int(
                        (latest.created_at + timedelta(minutes=2) - timezone.now()).total_seconds()
                    )
                    remaining = max(0, remaining)
                    messages.info(request, f"کد قبلی هنوز معتبر است. لطفاً {remaining} ثانیه صبر کنید.")
                    return redirect(reverse("register"))

                # باطل کردن کدهای قبلی و ساخت جدید
                PhoneOTP.objects.filter(user=user, is_used=False).update(is_used=True)
                otp_code = f"{random.randint(0, 999999):06d}"
                try:
                    PhoneOTP.objects.create(user=user, otp=otp_code)
                    send_otp_code(user.mobile, otp_code)
                    messages.success(request, "کد جدید ارسال شد.")
                except Exception as e:
                    logger.exception("Failed to send OTP to %s: %s", user.mobile, e)
                    messages.error(request, "ارسال کد با خطا مواجه شد. لطفاً بعداً تلاش کنید.")

                return redirect(reverse("register"))

            # --- Verify OTP ---
            form = OTPVerificationForm(request.POST)
            if form.is_valid():
                otp_entered = form.cleaned_data["otp"]
                otp_obj = PhoneOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()

                if not otp_obj:
                    messages.error(request, "کدی برای این شماره ارسال نشده است.")
                    return redirect(reverse("register"))

                if otp_obj.is_expired():
                    otp_obj.is_used = True
                    otp_obj.save(update_fields=["is_used"])
                    request.session.pop("pending_user_id", None)
                    messages.error(request, "کد تایید منقضی شده است. لطفاً دوباره شماره خود را وارد کنید.")
                    return redirect(reverse("register"))

                if otp_obj.otp == otp_entered:
                    otp_obj.is_used = True
                    otp_obj.save(update_fields=["is_used"])
                    user.is_active = True
                    if hasattr(user, "is_verified"):
                        user.is_verified = True
                        user.save(update_fields=["is_active", "is_verified"])
                    else:
                        user.save(update_fields=["is_active"])

                    request.session.pop("pending_user_id", None)
                    login(request, user)
                    return redirect("packages")

                messages.error(request, "کد وارد شده اشتباه است.")
                return redirect(reverse("register"))

        # --- GET نمایش فرم OTP ---
        return render(request, "register.html", {
            "form": OTPVerificationForm(),
            "step": "otp",
            "mobile": user.mobile,
            "cooldown_seconds": cooldown_seconds,
        })

    # --- Step 1: دریافت موبایل ---
    if request.method == "POST":
        form = MobileForm(request.POST)
        if form.is_valid():
            mobile = form.cleaned_data["mobile"]
            user, _ = User.objects.get_or_create(mobile=mobile, defaults={"is_active": False})

            otp_obj = PhoneOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()
            if otp_obj and not otp_obj.is_expired():
                messages.info(request, "کد قبلی هنوز معتبر است.")
                request.session["pending_user_id"] = user.id
                return redirect(reverse("register"))
            else:
                PhoneOTP.objects.filter(user=user, is_used=False).update(is_used=True)
                otp_code = f"{random.randint(0, 999999):06d}"
                try:
                    PhoneOTP.objects.create(user=user, otp=otp_code)
                    send_otp_code(mobile, otp_code)
                    messages.success(request, "کد تایید ارسال شد.")
                except Exception as e:
                    logger.exception("Failed to send OTP to %s: %s", mobile, e)
                    messages.error(request, "ارسال کد با خطا مواجه شد. لطفاً بعداً دوباره تلاش کنید.")
                    return redirect(reverse("register"))

                request.session["pending_user_id"] = user.id
                return redirect(reverse("register"))
    else:
        form = MobileForm()

    return render(request, "register.html", {"form": form, "step": "mobile"})


@login_required
def dashboard_view(request):
    user_plans = request.user.plans.select_related("plan")
    orders = request.user.orders.select_related("user")
    transactions = Payment.objects.filter(user=request.user).order_by("-created_at")[:5]  # تراکنش‌های واقعی
    plans_available = Plan.objects.filter(is_active=True)  # برای اضافه کردن پلن جدید

    return render(request, "dash.html", {
        "user_plans": user_plans,
        "orders": orders,
        "transactions": transactions,
        "plans_available": plans_available
    })


@login_required
def support(request):
    if request.method == "POST":
        form = SupportForm(request.POST)
        if form.is_valid():
            form.save()

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "redirect_url": "/dashboard/"})
            print("POST received")
            return redirect("dashboard")
        else:
            print("Form errors:", form.errors)
    else:
        form = SupportForm()
        print(form.errors)
    return render(request, "ticket.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("index")


def about(request):
    return render(request, "darbare.html")


def about_plans(request):
    return render(request, "about_plans.html")


def blog(request):
    return render(request, "blog.html")


def security(request):
    return render(request, "gavanin.html")
