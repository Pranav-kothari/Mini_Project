from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from .views import log_chat_message



urlpatterns = [
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('home/', views.home, name='home'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path("autocomplete/", views.product_autocomplete, name="product_autocomplete"),
    path('home/about/', views.about_view, name='about'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/increase_quantity/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease_quantity/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/product/add/', views.add_product, name='add_product'),
    path('seller/product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('seller/listing/<int:listing_id>/edit/', views.edit_listing, name='edit_listing'),
    path('seller/listing/<int:listing_id>/delete/', views.delete_listing, name='delete_listing'),
    path('cart/place_order/', views.place_order, name='place_order'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('chatbot/', views.chatbot_response, name='chatbot_response'),
    path('api/categories/', views.get_categories, name='get_categories'),
    path('api/subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    path('api/products/<int:subcategory_id>/', views.get_products, name='get_products'),
    path('api/price_range/<int:subcategory_id>/', views.get_price_range, name='get_price_range'),
    path('api/log_message/', log_chat_message, name='log_message'),
    path('add-address/', views.add_address, name='add_address'),
]
