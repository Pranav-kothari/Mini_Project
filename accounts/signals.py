from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Seller
from django.core.mail import send_mail
from django.conf import settings
from .models import ProductListing

# Create Profile when User is created
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Save Profile when User is saved
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

# Create Seller when Profile is updated to role='seller'
@receiver(post_save, sender=Profile)
def create_seller_for_profile(sender, instance, **kwargs):
    if instance.role == 'seller':
        Seller.objects.get_or_create(
            user=instance.user,
            defaults={
                'store_name': f"{instance.user.username}'s Store",
                'contact_number': '0000000000'
            }
        )
@receiver(post_save, sender=ProductListing)
def notify_listing_status(sender, instance, created, **kwargs):
    seller_email = instance.seller.user.email
    product_name = instance.product.name

    # 1. When a new product listing is created
    if created:
        subject = f"Product Listing Submitted: {product_name}"
        message = (
            f"Dear {instance.seller.store_name},\n\n"
            f"Your product '{product_name}' has been submitted for approval.\n"
            f"Supervisor Status: {instance.supervisor_status}, Admin Status: {instance.admin_status}.\n\n"
            "You will be notified when the product is reviewed.\n\n"
            "Regards,\nMyShopee Team"
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [seller_email])
        return

    # 2. Supervisor review
    if 'supervisor_status' in instance.__dict__:
        subject = f"Supervisor Update for: {product_name}"
        message = (
            f"Dear {instance.seller.store_name},\n\n"
            f"The supervisor has updated the status of your product '{product_name}' to: {instance.supervisor_status}.\n\n"
            "Regards,\nMyShopee Team"
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [seller_email])

    # 3. Admin review
    if 'admin_status' in instance.__dict__:
        subject = f"Admin Decision on: {product_name}"
        message = (
            f"Dear {instance.seller.store_name},\n\n"
            f"The admin has updated the status of your product '{product_name}' to: {instance.admin_status}.\n\n"
            "Regards,\nMyShopee Team"
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [seller_email])