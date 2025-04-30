from django.db import models
from django.contrib.auth.models import User

class UserMeasurement(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    chest = models.DecimalField(max_digits=5, decimal_places=2)  # Changed to DecimalField
    shoulder = models.DecimalField(max_digits=5, decimal_places=2)
    length = models.DecimalField(max_digits=5, decimal_places=2)
    sleeve_length = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Measurements for {self.user.username}"
