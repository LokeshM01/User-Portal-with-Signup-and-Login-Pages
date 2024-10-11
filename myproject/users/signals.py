from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import AdminActivityLog
from django.utils.timezone import now
from allauth.account.signals import user_signed_up

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AdminActivityLog.objects.create(
        user=user,
        action="User logged in",
        details=f"IP: {request.META.get('REMOTE_ADDR')}",
        timestamp=now()
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    AdminActivityLog.objects.create(
        user=user,
        action="User logged out",
        details=f"IP: {request.META.get('REMOTE_ADDR')}",
        timestamp=now()
    )
    
def log_user_signup(sender, request, user, **kwargs):
    AdminActivityLog.objects.create(
        user=user,
        action="User signed up",
        details=f"New user: {user.username}",
        timestamp=now()
    )
