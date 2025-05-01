from django import forms

class PreferenceSearchForm(forms.Form):
    search_term = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border-gray-300 shadow-sm',
            'placeholder': 'Enter search term...'
        })
    )
    shoulder_priority = forms.IntegerField(
        min_value=2,
        max_value=4,
        initial=2,
        widget=forms.NumberInput(attrs={'class': 'mt-1 border-gray-300 rounded-md w-full'})
    )
    length_priority = forms.IntegerField(
        min_value=2,
        max_value=4,
        initial=3,
        widget=forms.NumberInput(attrs={'class': 'mt-1 border-gray-300 rounded-md w-full'})
    )
    sleeve_priority = forms.IntegerField(
        min_value=2,
        max_value=4,
        initial=4,
        widget=forms.NumberInput(attrs={'class': 'mt-1 border-gray-300 rounded-md w-full'})
    )
