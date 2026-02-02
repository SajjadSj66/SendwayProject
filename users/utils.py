# from kavenegar import KavenegarAPI
#
# def send_otp_code(phone, otp):
#     api = KavenegarAPI('72746F6D576D4E46684476576E55443477356745757551585134305566755132304F3743735A4D666B73303D')
#     params = {
#         'sender': '2000660110',
#         'receptor': '09363772673',
#         'message': f"کد تایید شما: {otp}"
#     }
#     api.sms_send(params)


import requests
from django.conf import settings


class SmsIrError(Exception):
    pass


def send_otp_code(mobile: str, code: str) -> int:
    """
    ارسال کد تایید از طریق sms.ir
    بازمی‌گرداند: messageId در صورت موفقیت
    """
    # آدرس درست (بدون newline اضافی)
    url = "https://api.sms.ir/v1/send/verify"

    # گرفتن و پاک‌سازی API key از settings
    api_key = getattr(settings, "SMSIR_API_KEY", "")
    api_key = api_key.strip() if isinstance(api_key, str) else ""
    if not api_key:
        raise SmsIrError("API key برای SMS.ir تنظیم نشده یا خالی است")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-KEY": api_key,
    }

    # پاک‌سازی شماره (مثال: +989123456789 -> 09123456789)
    mobile = str(mobile).replace(" ", "").replace("+98", "0")
    if not mobile.startswith("0"):
        # در صورت لزوم این خط را تغییر دهید تا فرمت دلخواه شما را حفظ کند
        mobile = mobile

    payload = {
        "mobile": mobile,
        "templateId": int(getattr(settings, "SMSIR_TEMPLATE_ID", 0)),
        "parameters": [{"name": "code", "value": str(code)}],
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)

        # لاگ برای دیباگ — می‌توانید این‌ها را به logger منتقل کنید
        print("SMS.ir response:", resp.status_code, resp.text)

        # سعی می‌کنیم JSON را ایمن پارس کنیم
        content_type = resp.headers.get("Content-Type", "")
        data = {}
        if content_type.lower().startswith("application/json"):
            try:
                data = resp.json()
            except ValueError:
                data = {}

        # اگر 401 باشه پیغام مشخص بده
        if resp.status_code == 401:
            raise SmsIrError("احراز هویت ناموفق (401). لطفا API key و تنظیمات پنل SMS.ir را بررسی کنید.")

        # بررسی عمومی‌تر وضعیت
        if resp.status_code != 200 or data.get("status") != 1:
            raise SmsIrError(f"SMS.ir failed: http={resp.status_code}, body={data}")

        # برگشت messageId (ممکنه مسیرش فرق کنه؛ طبق پاسخ نمونه شما)
        return data["data"]["messageId"]

    except requests.RequestException as e:
        # خطاهای شبکه / timeout و غیره
        raise SmsIrError(f"خطای شبکه در ارسال به SMS.ir: {e}")
    except Exception as e:
        # سایر خطاها
        raise SmsIrError(str(e))
