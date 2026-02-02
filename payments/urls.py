from django.urls import path
from . import views

urlpatterns = [
    path("start/<int:order_id>/", views.start_payment, name="start_payment"),
    path("verify/<int:order_id>/", views.verify_payment, name="verify_payment"),
    # path("test-sms/", views.test_sms, name="test_sms"),
    path("transactions/", views.transactions, name="transactions"),
]
