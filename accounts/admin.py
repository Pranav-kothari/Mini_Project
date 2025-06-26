from django.contrib import admin
from .models import (
    Product, Category, Profile, Seller, 
    ProductListing, CartItem, Order, 
    OrderItem, Subcategory,Address
)
from .models import ChatbotLog


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Profile)
admin.site.register(Seller)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Subcategory)
admin.site.register(Address)

@admin.register(ProductListing)
class ProductListingAdmin(admin.ModelAdmin):
    list_display = ('product', 'seller', 'price', 'stock', 'is_approved')
    list_filter = ('is_approved', 'seller')
    actions = ['approve_listings']

    def approve_listings(self, request, queryset):
        updated_count = queryset.update(is_approved=True)
        self.message_user(request, f"{updated_count} product listing(s) approved.")
    approve_listings.short_description = "Approve selected product listings"



@admin.register(ChatbotLog)
class ChatbotLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'page', 'message_by', 'message')
    list_filter = ('page', 'message_by')
    search_fields = ('message',)
