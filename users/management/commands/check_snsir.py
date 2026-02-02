# yourapp/management/commands/check_smsir.py
import os
import json
import requests
from django.core.management.base import BaseCommand
from django.conf import settings

def mask(s):
    if not s:
        return "<EMPTY>"
    s = str(s)
    if len(s) <= 8:
        return "****"
    return s[:4] + "..." + s[-4:]

class Command(BaseCommand):
    help = "Check SMS.ir config (masked key), public IP, proxy envs and do a test POST to sms.ir"

    def add_arguments(self, parser):
        parser.add_argument('--mobile', help='Mobile number to test (e.g. 0912xxxxxxx)', required=False)
        parser.add_argument('--template', type=int, help='Override templateId for test', required=False)

    def handle(self, *args, **options):
        self.stdout.write("=== SMS.ir config checker ===")
        # settings info
        self.stdout.write("Django settings module: %s" % getattr(settings, '__name__', 'unknown'))
        try:
            self.stdout.write("settings file: %s" % getattr(settings, '__file__', 'unknown'))
        except Exception:
            pass

        api_key = getattr(settings, "SMSIR_API_KEY", None)
        self.stdout.write("SMSIR_API_KEY present in settings: %s" % bool(api_key))
        self.stdout.write("masked key (settings): %s" % mask(api_key))

        # Also check env var directly
        env_key = os.environ.get("SMSIR_API_KEY")
        self.stdout.write("SMSIR_API_KEY present in ENV: %s" % bool(env_key))
        self.stdout.write("masked key (env): %s" % mask(env_key))

        # template id
        tmpl = getattr(settings, "SMSIR_TEMPLATE_ID", None)
        self.stdout.write("SMSIR_TEMPLATE_ID in settings: %r" % tmpl)

        # proxy envs
        self.stdout.write("--- Proxy env vars ---")
        for v in ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"):
            self.stdout.write("%s = %r" % (v, os.environ.get(v)))

        # get public ip
        self.stdout.write("--- Public IP check ---")
        try:
            r = requests.get("https://api.ipify.org?format=json", timeout=10)
            if r.status_code == 200:
                ip = r.json().get("ip")
                self.stdout.write("Public IP (api.ipify.org): %s" % ip)
            else:
                self.stdout.write("api.ipify returned status %s body=%s" % (r.status_code, r.text[:500]))
        except Exception as e:
            self.stdout.write("Could not get public IP: %s" % e)

        # if no mobile passed, skip POST test
        mobile = options.get("mobile")
        if not mobile:
            self.stdout.write(self.style.WARNING("No --mobile provided; skipping POST test."))
            self.stdout.write("To run test POST: python manage.py check_smsir --mobile 0912xxxxxxx")
            return

        # normalize mobile and template
        mobile_norm = str(mobile).replace(" ", "").replace("+98", "0")
        template_id = options.get("template") or int(getattr(settings, "SMSIR_TEMPLATE_ID", 0) or 0)

        payload = {
            "mobile": mobile_norm,
            "templateId": template_id,
            "parameters": [{"name": "code", "value": "1234"}],
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-KEY": api_key or os.environ.get("SMSIR_API_KEY", "") or "",
        }

        self.stdout.write("--- Performing TEST POST to https://api.sms.ir/v1/send/verify ---")
        self.stdout.write("Request payload (mobile, templateId): %s, %s" % (mobile_norm, template_id))
        try:
            resp = requests.post("https://api.sms.ir/v1/send/verify", json=payload, headers=headers, timeout=10)
            self.stdout.write("Response status: %s" % resp.status_code)
            # print body (truncated)
            body = resp.text or ""
            if len(body) > 1500:
                body = body[:1500] + " ... (truncated)"
            self.stdout.write("Response body: %s" % body)
            try:
                self.stdout.write("Parsed JSON: %s" % json.dumps(resp.json(), ensure_ascii=False))
            except Exception:
                pass
        except Exception as e:
            self.stdout.write("POST request exception: %s" % e)
