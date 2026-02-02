from django.urls import path
from . import views

# app_name = "plans"
urlpatterns = [
    # نمایش پلن‌ها
    path("packages/", views.plan_list, name="packages"),
    path("add/<int:plan_id>/", views.add_to_order, name="add_to_order"),

    path("checkout/", views.checkout, name="checkout"),
    # path('merge/', views.merge_cart, name='merge_cart'),
    path("item/<int:item_id>/remove/", views.remove_item, name="remove_item"),

    # مدیریت آیتم‌ها
    path("item/<int:item_id>/<str:action>/", views.update_item_quantity, name="update_item_quantity"),

    # لیست سفارش‌های کاربر (transactions)
    path('orders/', views.order_list, name='orders'),
]
