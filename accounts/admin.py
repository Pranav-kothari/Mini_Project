from django.contrib import admin
from .models import (
    Product, Category, Profile, Seller, 
    ProductListing, CartItem, Order, 
    OrderItem, Subcategory, Address,ProductReview
)
from .models import ChatbotLog
from .models import WishlistRequest


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Profile)
admin.site.register(Seller)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Subcategory)
admin.site.register(Address)
admin.site.register(ProductReview)

@admin.register(ProductListing)
class ProductListingAdmin(admin.ModelAdmin):
    list_display = ('product', 'seller', 'price', 'stock', 'status', 'listed_date')
    list_filter = ('supervisor_status', 'admin_status', 'seller')
    actions = ['approve_listings', 'reject_listings']

    def approve_listings(self, request, queryset):
        updated_count = queryset.update(supervisor_status='approved', admin_status='approved')
        self.message_user(request, f"{updated_count} product listing(s) approved.")
    approve_listings.short_description = "Approve selected product listings"

    def reject_listings(self, request, queryset):
        updated_count = queryset.update(supervisor_status='rejected', admin_status='rejected')
        self.message_user(request, f"{updated_count} product listing(s) rejected.")
    reject_listings.short_description = "Reject selected product listings"


@admin.register(ChatbotLog)
class ChatbotLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'page', 'message_by', 'message')
    list_filter = ('page', 'message_by')
    search_fields = ('message',)


@admin.action(description='Mark selected requests as Approved')
def approve_requests(modeladmin, request, queryset):
    queryset.update(status='approved')

@admin.action(description='Mark selected requests as Rejected')
def reject_requests(modeladmin, request, queryset):
    queryset.update(status='rejected')

@admin.register(WishlistRequest)
class WishlistRequestAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'user', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['product_name', 'user__username']
    actions = [approve_requests, reject_requests]  # 👈 Add this line

