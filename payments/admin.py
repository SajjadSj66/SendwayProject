from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "order", "amount", "gateway", "status", "created_at")
    search_fields = ("user__mobile", "track_id", "ref_id", "description")
    list_filter = ("status", "gateway", "created_at")
    ordering = ("-created_at",)

    readonly_fields = ("created_at",)

    fieldsets = (
        ("اطلاعات کاربر و سفارش", {"fields": ("user", "order")}),
        ("جزئیات پرداخت", {"fields": ("amount", "gateway", "status")}),
        ("اطلاعات تراکنش", {"fields": ("track_id", "ref_id", "description")}),
        ("زمان", {"fields": ("created_at",)}),
    )

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "مدیریت پرداخت‌ها"
