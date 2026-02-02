import requests
from SendWayProject import settings


def notify_admin_new_order(order):
    api_key = settings.SMSIR_API_KEY
    url = "https://api.sms.ir/v1/send/verify"  # دقت کن فرق کرد

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }

    items = ", ".join([f"{item.plan.id} - {item.plan.title} × {item.quantity}" for item in order.items.all()])

    payload = {
        "mobile": "09052427494",  # شماره ادمین
        "templateId": int(settings.TEMPLATE_ID),
        "parameters": [
            {"name": "ORDER.USER.MOBILE", "value": order.user.mobile},
            {"name": "ORDER.TOTAL_PRICE", "value": str(order.total_price)},
            {"name": "ITEMS", "value": items},
        ]
    }

    response = requests.post(url, json=payload, headers=headers, verify=True)
    print("SMS Response:", response.status_code, response.text)
    try:
        return response.json()
    except ValueError:
        return {"status_code": response.status_code, "text": response.text}


def send_template_sms(mobile: str, template_id: int, parameters: list):
    """
    ارسال SMS با template در sms.ir
    parameters: لیستی از دیکشنری‌ها با keys: name, value
    مثال: [{"name": "ORDER.USER.MOBILE", "value": "0901..."}, ...]
    """
    api_key = settings.SMSIR_API_KEY
    url = "https://api.sms.ir/v1/send/verify"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }

    payload = {
        "mobile": mobile,
        "templateId": int(template_id),
        "parameters": parameters,
    }

    resp = requests.post(url, json=payload, headers=headers, verify=True)
    try:
        return resp.json()
    except ValueError:
        # اگر پاسخ JSON نبود، متن خام را برگردان
        return {"status_code": resp.status_code, "text": resp.text}
