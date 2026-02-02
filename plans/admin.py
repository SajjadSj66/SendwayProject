from django.contrib import admin
from .models import Plan, UserPlan, Order, OrderItem


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("category", "price", "is_active")
    search_fields = ("category", "description", "features")
    list_filter = ("is_active",)
    ordering = ("-id",)

    class Meta:
        verbose_name = "پلن"
        verbose_name_plural = "مدیریت پلن‌ها"


@admin.register(UserPlan)
class UserPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "start_date")
    search_fields = ("user__mobile", "plan__title")
    list_filter = ("start_date",)
    ordering = ("-start_date",)

    class Meta:
        verbose_name = "پلن کاربر"
        verbose_name_plural = "پلن‌های کاربران"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('plan_title', 'plan_category', 'quantity')
    fields = ('plan_title', 'plan_category', 'quantity')  # نمایش ستون‌ها
    can_delete = False  # اگر نمی‌خوای حذف بشن

    # اگر بخوای فقط نمایش بده و ویرایش نکنه
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "user",  # کاربری که سفارش داده
        "first_name",
        "last_name",
        "phone",
        "total_price",
        "status",
        "created_at",
    )
    search_fields = ("user__mobile", "first_name", "last_name", "phone")
    list_filter = ("status", "created_at")
    ordering = ("-created_at",)
    readonly_fields = (
        "user",
        "first_name",
        "last_name",
        "phone",
        "instagram",
        "notes",
        "total_price",
        "status",
        "created_at",
    )
    inlines = [OrderItemInline]

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "مدیریت سفارش‌ها"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ( "plan", "quantity", "total_price")
    search_fields = ("order__total_price", "plan__category")
    list_filter = ("order__created_at",)

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "مدیریت آیتم ها"
