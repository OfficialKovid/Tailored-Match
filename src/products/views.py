from django.views.generic import ListView
from .models import Shirt
from django.db.models import Q

class ShirtListView(ListView):
    model = Shirt
    template_name = 'products/shirt_list.html'
    context_object_name = 'shirts'

    def get_queryset(self):
        queryset = Shirt.objects.all()
        fit_type = self.request.GET.get('fit', 'all')
        
        # Get user measurements from session
        user_measurements = self.request.session.get('user_measurements', {})
        
        if fit_type != 'all':
            queryset = queryset.filter(Q(title__icontains=fit_type))
        
        # Calculate match scores and sort
        shirts_with_data = []
        for shirt in queryset:
            match_score = shirt.get_size_match_score(user_measurements)
            best_size = shirt.get_best_matching_size(user_measurements)
            sizes_with_measurements = shirt.get_sizes_with_measurements()
            shirts_with_data.append((shirt, match_score, best_size, sizes_with_measurements))
        
        # Sort by match score, highest first
        shirts_with_data.sort(key=lambda x: x[1], reverse=True)
        
        return [(shirt, best_size, sizes_with_measurements) 
                for shirt, score, best_size, sizes_with_measurements in shirts_with_data]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_fit'] = self.request.GET.get('fit', 'all')
        context['fit_types'] = [
            'Regular Fit',
            'Slim Fit',
            'Comfort Fit', 
            'Relaxed Fit',
            'Tailored Fit'
        ]
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
