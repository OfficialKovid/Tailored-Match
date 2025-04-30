from django.urls import path
from .views import ShirtListView, AllProductsView

app_name = 'products'

urlpatterns = [
    path('shirts/', ShirtListView.as_view(), name='shirt_list'),
    path('all-products/', AllProductsView.as_view(), name='all_products'),
]
