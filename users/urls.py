from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('ticket/', views.support, name='ticket'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.about, name='about'),
    path('about_plans/', views.about_plans, name='about_plans'),
    path('blog/', views.blog, name='blog'),
    path('security/', views.security, name='security'),
]
