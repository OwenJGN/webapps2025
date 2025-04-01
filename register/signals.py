from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create a user profile when a user is created.

    Args:
        sender: The model class that sent the signal
        instance: The actual instance being saved
        created: Boolean; True if a new record was created
    """
    if created:
        # Only create profile if it doesn't exist
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Signal handler to save the user profile when a user is saved.

    Args:
        sender: The model class that sent the signal
        instance: The actual instance being saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()