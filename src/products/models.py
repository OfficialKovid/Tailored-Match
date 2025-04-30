from django.db import models
import json

class Shirt(models.Model):
    pid = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=200)
    price = models.CharField(max_length=20)
    rating = models.FloatField(null=True, blank=True)
    sizes_listed = models.TextField()  # Will store as JSON string
    img_url = models.URLField(max_length=500)
    url = models.URLField(max_length=500)

    def __str__(self):
        return f"{self.title} ({self.pid})"

    @property
    def size_list(self):
        return json.loads(self.sizes_listed)

    def save_size_data(self, size_chart_data):
        """Save size chart data for this shirt"""
        for size_name, measurements in size_chart_data.items():
            size_obj, _ = Size.objects.get_or_create(
                shirt=self,
                size_name=size_name
            )
            
            SizeChart.objects.update_or_create(
                size=size_obj,
                defaults={
                    'chest': measurements.get('chest'),
                    'shoulder': measurements.get('shoulder'), 
                    'length': measurements.get('length'),
                    'sleeve_length': measurements.get('sleeve-length')
                }
            )

    def get_size_match_score(self, user_measurements):
        """Calculate how well this shirt matches user measurements"""
        if not user_measurements:
            return 0
            
        best_match_score = 0
        user_chest = float(user_measurements.get('chest', 0))
        user_shoulder = float(user_measurements.get('shoulder', 0))
        
        for size in self.sizes.all():
            if hasattr(size, 'measurements'):
                measurements = size.measurements
                if not measurements:
                    continue
                    
                chest_diff = abs(float(measurements.chest or 0) - user_chest)
                shoulder_diff = abs(float(measurements.shoulder or 0) - user_shoulder)
                
                # Calculate match score (inverse of difference - smaller difference means better match)
                match_score = 100 - (chest_diff + shoulder_diff) * 2
                match_score = max(0, match_score)  # Ensure score doesn't go negative
                
                # Keep track of best matching size
                best_match_score = max(best_match_score, match_score)
                
        return best_match_score

    class Meta:
        db_table = 'shirts'
        verbose_name = 'Shirt'
        verbose_name_plural = 'Shirts'

class Size(models.Model):
    shirt = models.ForeignKey(Shirt, on_delete=models.CASCADE, related_name='sizes')
    size_name = models.CharField(max_length=10)  # S, M, L, XL etc

    def __str__(self):
        return f"{self.shirt.pid} - {self.size_name}"
    
    class Meta:
        unique_together = ('shirt', 'size_name')

class SizeChart(models.Model):
    size = models.OneToOneField(Size, on_delete=models.CASCADE, related_name='measurements')
    chest = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    shoulder = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sleeve_length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Measurements for {self.size}"
