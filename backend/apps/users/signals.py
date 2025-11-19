from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.customers.services import auto_link_customer_for_user
from django.core.files.storage import default_storage
from apps.users.models import UserProfile


@receiver(post_save, sender=get_user_model())
def link_customer_on_user_create(sender, instance, created, **kwargs):
    if created:
        auto_link_customer_for_user(instance)

@receiver(pre_save, sender=UserProfile)
def delete_old_avatar_on_change(sender, instance: UserProfile, **kwargs):
    if not instance.pk:
        return
    try:
        old = UserProfile.objects.get(pk=instance.pk)
    except UserProfile.DoesNotExist:
        return
    if old.avatar and old.avatar != instance.avatar:
        try:
            default_storage.delete(old.avatar.name)
        except Exception:
            pass
    if getattr(old, "avatar_thumb", None) and old.avatar_thumb != getattr(instance, "avatar_thumb", None):
        try:
            default_storage.delete(old.avatar_thumb.name)
        except Exception:
            pass

@receiver(post_delete, sender=UserProfile)
def delete_avatar_files_on_delete(sender, instance: UserProfile, **kwargs):
    if instance.avatar:
        try:
            default_storage.delete(instance.avatar.name)
        except Exception:
            pass
    if getattr(instance, "avatar_thumb", None):
        try:
            default_storage.delete(instance.avatar_thumb.name)
        except Exception:
            pass


