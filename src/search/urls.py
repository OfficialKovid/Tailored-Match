from django.urls import path
from .views import PreferenceSearchView

app_name = 'search'

urlpatterns = [
    path('preference/', PreferenceSearchView.as_view(), name='preference_search'),
]
