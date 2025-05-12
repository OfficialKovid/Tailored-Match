from django.contrib import admin
from .models import Shirt, Size, SizeChart

class SizeChartInline(admin.TabularInline):
    model = SizeChart
    extra = 1

class SizeAdmin(admin.ModelAdmin):
    inlines = [SizeChartInline]
    list_display = ['shirt', 'size_name']
    search_fields = ['shirt__pid', 'shirt__title', 'size_name']

class SizeInline(admin.TabularInline):
    model = Size
    extra = 1

class ShirtAdmin(admin.ModelAdmin):
    inlines = [SizeInline]
    list_display = ['pid', 'title', 'price', 'rating']
    search_fields = ['pid', 'title']
    list_filter = ['rating']

admin.site.register(Shirt, ShirtAdmin)
admin.site.register(Size, SizeAdmin)
