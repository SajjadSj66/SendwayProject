from django.db import models
from plans.models import Order
from users.models import User


# Create your models here.
class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار'),
        ('success', 'موفق'),
        ('failed', 'ناموفق'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ")
    gateway = models.CharField(max_length=50, verbose_name="درگاه پرداخت", default="zibal")

    track_id = models.CharField(max_length=100, verbose_name="شناسه تراکنش (trackId)", blank=True, null=True)
    ref_id = models.CharField(max_length=100, verbose_name="کد پیگیری (refNumber)", blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.CharField(max_length=255, verbose_name="توضیحات", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" پرداخت{self.user} - {self.amount} ({self.status})"

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"
