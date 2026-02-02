from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from datetime import timedelta
from django.utils import timezone


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, mobile, **extra_fields):
        if not mobile:
            raise ValueError('شماره موبایل خود را وارد کنید')
        extra_fields.setdefault('is_active', False)  # مهم!
        user = self.model(mobile=mobile, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(mobile, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    mobile = models.CharField(max_length=11, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    data_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.mobile

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.mobile

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"


class PhoneOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=2)

    def __str__(self):
        return f"{self.user.mobile} - {self.otp}"


class Support(models.Model):
    DEPARTMENTS = [
        ('support', 'پشتیبانی فنی'),
        ('finance', 'امور مالی'),
        ('orders', 'سفارش‌ها'),
    ]

    STATUS_CHOICES = (
        ('open', 'باز'),
        ('in_progress', 'در حال بررسی'),
        ('closed', 'بسته شده'),
    )

    full_name = models.CharField(max_length=100, verbose_name="نام و نام خانوادگی", blank=True)
    subject = models.CharField(max_length=200, verbose_name="موضوع")
    phone = models.CharField(max_length=11, verbose_name="موبایل")
    email = models.EmailField(default='')
    message = models.TextField(verbose_name="متن تیکت")
    department = models.CharField(max_length=20, choices=DEPARTMENTS, default='support')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.subject}"

    class Meta:
        verbose_name = "تیکت"
        verbose_name_plural = "تیکت‌ها"
