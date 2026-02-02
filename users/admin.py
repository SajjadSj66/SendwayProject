from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Support


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # ستون‌هایی که در لیست نمایش داده می‌شن
    list_display = ("mobile", "first_name", "last_name", "is_active", "is_verified", "is_staff", "data_joined")
    list_filter = ("is_active", "is_verified", "is_staff")
    search_fields = ("mobile", "first_name", "last_name")
    ordering = ("-data_joined",)

    # برای فرم داخل ادمین
    fieldsets = (
        ("اطلاعات کاربری", {"fields": ("mobile", "first_name", "last_name", "password")}),
        ("دسترسی‌ها", {"fields": ("is_active", "is_verified", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("تاریخ‌ها", {"fields": ("data_joined",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("mobile", "password1", "password2", "is_active", "is_staff", "is_superuser"),
        }),
    )

    readonly_fields = ("data_joined",)

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "مدیریت کاربران"


@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = ("full_name", "subject", "status", "created_at")
    search_fields = ("phone", "subject", "message")
    list_filter = ("status", "created_at")
    ordering = ("-created_at",)

    class Meta:
        verbose_name = "تیکت"
        verbose_name_plural = "مدیریت تیکت‌ها"
