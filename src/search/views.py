from django.views.generic import FormView
from django.db.models import Q
from products.models import Shirt
from .forms import PreferenceSearchForm

class PreferenceSearchView(FormView):
    template_name = 'search/preference_search.html'
    form_class = PreferenceSearchForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['measurements'] = [
            ('chest', 'Chest'),
            ('shoulder', 'Shoulder'),
            ('length', 'Length'),
            ('sleeve_length', 'Sleeve Length')
        ]
        return context

    def form_valid(self, form):
        search_term = form.cleaned_data['search_term']
        priorities = {
            'chest': 1,  # Always first priority
            'shoulder': form.cleaned_data['shoulder_priority'],
            'length': form.cleaned_data['length_priority'],
            'sleeve_length': form.cleaned_data['sleeve_priority'],
        }

        # Get user measurements
        user_measurements = self.request.session.get('user_measurements', {})
        if not user_measurements:
            return self.render_to_response(self.get_context_data(
                error="Please enter your measurements first"
            ))

        # Search shirts
        shirts = Shirt.objects.filter(
            Q(title__icontains=search_term) |
            Q(sizes_listed__icontains=search_term)
        )

        # Calculate match scores with priorities
        shirts_with_scores = []
        for shirt in shirts:
            best_size, best_score = self.calculate_best_size(
                shirt, user_measurements, priorities
            )
            if best_size:
                shirts_with_scores.append((shirt, best_size, best_score))

        # Sort by match score
        shirts_with_scores.sort(key=lambda x: x[2], reverse=True)
        
        return self.render_to_response(self.get_context_data(
            results=shirts_with_scores[:40],
            search_term=search_term,
            priorities=priorities
        ))

    def calculate_best_size(self, shirt, measurements, priorities):
        best_size = None
        best_score = -1

        for size in shirt.sizes.all():
            if not hasattr(size, 'measurements'):
                continue
                
            m = size.measurements
            if not m:
                continue

            score = 0
            # Weight differences by priority (4 to 1)
            if m.chest and 'chest' in measurements:
                diff = abs(float(m.chest) - float(measurements['chest']))
                score += (5 - priorities['chest']) * (100 - diff)
                
            if m.shoulder and 'shoulder' in measurements:
                diff = abs(float(m.shoulder) - float(measurements['shoulder']))
                score += (5 - priorities['shoulder']) * (100 - diff)
                
            if m.length and 'length' in measurements:
                diff = abs(float(m.length) - float(measurements['length']))
                score += (5 - priorities['length']) * (100 - diff)
                
            if m.sleeve_length and 'sleeve_length' in measurements:
                diff = abs(float(m.sleeve_length) - float(measurements['sleeve_length']))
                score += (5 - priorities['sleeve_length']) * (100 - diff)

            if score > best_score:
                best_score = score
                best_size = size.size_name

        return best_size, best_score
