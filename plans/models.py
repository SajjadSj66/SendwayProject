from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Plan(models.Model):
    CATEGORIES_STATUS_CHOICE = (
        ('کاربران تصادفی', "کاربران تصادفی"),
        ('لایک کننده', 'لایک کننده'),
        ('کامنت‌گذار', 'کامنت‌گذار'),
        ('هشتگ', 'هشتگ'),
        ('لوکیشن', 'لوکیشن'),
        ('اکسپلور', 'اکسپلور'),
    )
    title = models.CharField(max_length=200, verbose_name="عنوان پلن", default="")
    category = models.CharField(max_length=100, choices=CATEGORIES_STATUS_CHOICE, default='کاربران تصادفی')
    description = models.TextField(verbose_name="توضیحات", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="قیمت")
    features = models.TextField(verbose_name="ویژگی‌ها")  # لیست امکانات هر پلن
    is_active = models.BooleanField(default=True, verbose_name="فعال/غیرفعال")

    def formatted_price(self):
        return "{:,}".format(int(self.price)).replace(",", "/")

    def __str__(self):
        return f"{self.title} -  {self.get_category_display()}"

    class Meta:
        verbose_name = "پلن"
        verbose_name_plural = "پلن‌ها"


class UserPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plans")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="subscriptions")
    start_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.mobile} - {self.plan.category}"

    class Meta:
        verbose_name = "پلن کاربر"
        verbose_name_plural = "پلن‌های کاربران"


class Order(models.Model):
    STATUS_CHOICES = (
        ('draft', 'پیش‌نویس'),
        ('submitted', 'ثبت‌شده'),
        ('paid', 'پرداخت‌شده'),
        ('canceled', 'لغوشده'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    phone = models.CharField(max_length=11, null=True, blank=True)  # از User میاد
    instagram = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    terms = models.BooleanField(default=False)

    total_price = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

    def formatted_total_price(self):
        return "{:,}".format(int(self.total_price)).replace(",", "/")

    def update_total_price(self):
        total = sum((item.total_price for item in self.items.all()), Decimal('0'))
        self.total_price = total
        self.save()

    def __str__(self):
        return f"Order #{self.id} - {self.user} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=0)

    def formatted_total_price(self):
        return "{:,}".format(int(self.total_price)).replace(",", "/")

    def save(self, *args, **kwargs):
        self.total_price = self.plan.price * self.quantity
        super().save(*args, **kwargs)
        # به‌روزرسانی مجموع سفارش
        if self.order_id:
            self.order.update_total_price()

    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        order.update_total_price()

    @property
    def plan_title(self):
        return self.plan.title

    @property
    def plan_category(self):
        return self.plan.category


def __str__(self):
    return f"{self.plan.title} x {self.quantity}"
