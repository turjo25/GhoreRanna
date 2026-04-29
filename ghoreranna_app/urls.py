from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('menu/', views.menu_list, name='menu_list'),
    path('menu/add/', views.menu_add, name='menu_add'),
    path('menu/<int:pk>/', views.menu_detail, name='menu_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:pk>/', views.cart_update, name='cart_update'),
    path('menu/<int:pk>/edit/', views.menu_update, name='menu_update'),
    path('menu/<int:pk>/delete/', views.menu_delete, name='menu_delete'),
    path('profile/', views.profile_view, name='profile'),
    # Checkout & Payment
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-confirmation/', views.order_confirmation_view, name='order_confirmation'),
    # Admin Cook Management
    path('manage-cooks/', views.cook_list, name='cook_list'),
    path('manage-cooks/add/', views.cook_create, name='cook_add'),
    path('manage-cooks/<int:pk>/edit/', views.cook_update, name='cook_edit'),
    path('manage-cooks/<int:pk>/delete/', views.cook_delete, name='cook_delete'),
    # Cook Order Management
    path('order/<int:pk>/update/', views.update_order_status, name='update_order_status'),
    path('order/<int:pk>/mark-delivered/', views.mark_order_delivered, name='mark_order_delivered'),
    path('order/<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
    path('validate-coupon/', views.validate_coupon, name='validate_coupon'),
    # Delivery Staff
    path('delivery/dashboard/', views.delivery_dashboard_view, name='delivery_dashboard'),
    path('delivery/<int:pk>/update-status/', views.delivery_update_status, name='delivery_update_status'),
    # Admin Coupon Management
    path('manage-coupons/add/', views.coupon_add, name='coupon_add'),
    path('manage-coupons/<int:pk>/edit/', views.coupon_edit, name='coupon_edit'),
    path('manage-coupons/<int:pk>/delete/', views.coupon_delete, name='coupon_delete'),
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
]