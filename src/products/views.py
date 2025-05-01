from django.views.generic import ListView
from django.core.paginator import Paginator
from .models import Shirt
from django.db.models import Q
import re

class ShirtListView(ListView):
    model = Shirt
    template_name = 'products/shirt_list.html'
    context_object_name = 'shirts'
    paginate_by = 40

    def get_price_value(self, price_str):
        """Extract numeric value from price string"""
        if not price_str:
            return 0
        return float(re.sub(r'[^\d.]', '', price_str))

    def get_queryset(self):
        queryset = Shirt.objects.all()
        
        # Get filter parameters
        fit_type = self.request.GET.get('fit', 'all')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        min_rating = self.request.GET.get('min_rating')
        sort_by = self.request.GET.get('sort', 'match')

        # Get priorities
        priorities = {
            'chest': 1,  # Always first priority
            'shoulder': int(self.request.GET.get('shoulder_priority', 2)),
            'length': int(self.request.GET.get('length_priority', 3)),
            'sleeve_length': int(self.request.GET.get('sleeve_priority', 4)),
        }
        
        # Apply filters
        if fit_type != 'all':
            queryset = queryset.filter(Q(title__icontains=fit_type))
        
        # Filter prices in Python instead of SQL
        shirts = list(queryset)
        if min_price:
            min_price_value = float(min_price)
            shirts = [shirt for shirt in shirts if self.get_price_value(shirt.price) >= min_price_value]
        
        if max_price:
            max_price_value = float(max_price)
            shirts = [shirt for shirt in shirts if self.get_price_value(shirt.price) <= max_price_value]
            
        if min_rating:
            shirts = [shirt for shirt in shirts if shirt.rating and shirt.rating >= float(min_rating)]

        # Calculate scores with priorities
        user_measurements = self.request.session.get('user_measurements', {})
        shirts_with_data = []
        
        for shirt in shirts:
            score = 0
            best_size = None
            sizes_with_measurements = shirt.get_sizes_with_measurements()

            for size in shirt.sizes.all():
                if not hasattr(size, 'measurements'):
                    continue
                    
                m = size.measurements
                if not m:
                    continue

                size_score = 0
                # Weight differences by priority (4 to 1)
                if m.chest and 'chest' in user_measurements:
                    diff = abs(float(m.chest) - float(user_measurements['chest']))
                    size_score += (5 - priorities['chest']) * (100 - diff)
                
                if m.shoulder and 'shoulder' in user_measurements:
                    diff = abs(float(m.shoulder) - float(user_measurements['shoulder']))
                    size_score += (5 - priorities['shoulder']) * (100 - diff)
                
                if m.length and 'length' in user_measurements:
                    diff = abs(float(m.length) - float(user_measurements['length']))
                    size_score += (5 - priorities['length']) * (100 - diff)
                
                if m.sleeve_length and 'sleeve_length' in user_measurements:
                    diff = abs(float(m.sleeve_length) - float(user_measurements['sleeve_length']))
                    size_score += (5 - priorities['sleeve_length']) * (100 - diff)

                if size_score > score:
                    score = size_score
                    best_size = size.size_name

            shirts_with_data.append((shirt, best_size, score, sizes_with_measurements))
        
        # Sort based on selected criteria
        if sort_by == 'price_low':
            shirts_with_data.sort(key=lambda x: self.get_price_value(x[0].price))
        elif sort_by == 'price_high':
            shirts_with_data.sort(key=lambda x: self.get_price_value(x[0].price), reverse=True)
        elif sort_by == 'rating':
            shirts_with_data.sort(key=lambda x: x[0].rating or 0, reverse=True)
        else:  # sort by match score
            shirts_with_data.sort(key=lambda x: x[2], reverse=True)
        
        return [(shirt, best_size, sizes_with_measurements) 
                for shirt, best_size, score, sizes_with_measurements in shirts_with_data]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'current_fit': self.request.GET.get('fit', 'all'),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'min_rating': self.request.GET.get('min_rating', ''),
            'sort_by': self.request.GET.get('sort', 'match'),
            'fit_types': [
                'Regular Fit',
                'Slim Fit',
                'Comfort Fit', 
                'Relaxed Fit',
                'Tailored Fit'
            ],
            'show_filters': bool(
                self.request.GET.get('min_price') or
                self.request.GET.get('max_price') or
                self.request.GET.get('min_rating') or
                self.request.GET.get('sort') or
                self.request.GET.get('fit') != 'all'
            ),
            'shoulder_priority': self.request.GET.get('shoulder_priority', '2'),
            'length_priority': self.request.GET.get('length_priority', '3'),
            'sleeve_priority': self.request.GET.get('sleeve_priority', '4'),
        })
        return context

class AllProductsView(ListView):
    model = Shirt
    template_name = 'see_all_products.html'
    context_object_name = 'products'
    paginate_by = 40

    def get_queryset(self):
        return Shirt.objects.all().prefetch_related('sizes__measurements')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = Shirt.objects.count()
        return context
