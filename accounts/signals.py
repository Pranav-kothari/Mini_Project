from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Seller

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
