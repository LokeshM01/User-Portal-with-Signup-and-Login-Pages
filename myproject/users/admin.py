from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.html import format_html
from .models import Customer 
from .models import AdminActivityLog 

class CustomUserAdmin(UserAdmin):
    # Display additional fields in the admin interface
    list_display = ('username', 'email', 'first_name', 'last_name', 'display_profile_picture')

    # Add the google_profile_picture to the user admin detail view
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('google_profile_picture',)}),
    )

    # This method displays the profile picture as an image in the list view
    def display_profile_picture(self, obj):
        if obj.google_profile_picture:
            return format_html('<img src="{}" width="50" height="50" />', obj.google_profile_picture)
        return "No picture"
    
    display_profile_picture.short_description = 'Profile Picture'


@admin.register(AdminActivityLog)  # Register the model with the admin
class AdminActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    search_fields = ('user__username', 'action', 'details')
    list_filter = ('action', 'timestamp')

# Register the CustomUser model with the CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Customer)
