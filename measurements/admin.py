from django.contrib import admin
from .models import UserMeasurement

class UserMeasurementAdmin(admin.ModelAdmin):
    list_display = ['user', 'chest', 'shoulder', 'length', 'sleeve_length', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(UserMeasurement, UserMeasurementAdmin)
