from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserMeasurement
from decimal import Decimal

@login_required(login_url='/login/')
def enter_measurements(request):
    if request.method == 'POST':
        measurements = {
            'chest': request.POST.get('chest'),
            'shoulder': request.POST.get('shoulder'),
            'length': request.POST.get('length'),
            'sleeve_length': request.POST.get('sleeve_length')
        }
        
        # Validate measurements
        try:
            for key, value in measurements.items():
                measurements[key] = Decimal(value)
                if measurements[key] <= 0:
                    raise ValueError(f"{key.replace('_', ' ').title()} must be greater than 0")
                    
        except (TypeError, ValueError) as e:
            messages.error(request, str(e) or 'Please enter valid measurements')
            return redirect('measurements:enter_measurements')

        # Save to database
        user_measurement, created = UserMeasurement.objects.update_or_create(
            user=request.user,
            defaults=measurements
        )
        
        # Store in session
        request.session['user_measurements'] = {
            key: str(value) for key, value in measurements.items()
        }
        
        messages.success(request, 'Measurements saved successfully!')
        return redirect('products:shirt_list')

    # For GET request, show the form with existing measurements
    try:
        current_measurements = UserMeasurement.objects.get(user=request.user)
    except UserMeasurement.DoesNotExist:
        current_measurements = None

    return render(request, 'measurements/enterMeasurement.html', {
        'current_measurements': current_measurements
    })