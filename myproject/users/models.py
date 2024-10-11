from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from django.conf import settings 


class CustomUser(AbstractUser):
    google_profile_picture = models.URLField(blank=True, null=True)


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    birthdate = models.DateField(null=True, blank=True) 
    country_code = models.CharField(max_length=5, default='+91')
    pdf_file_path = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
class AdminActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)  # Use AUTH_USER_MODEL
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=now)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"