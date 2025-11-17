from django import forms
from .models import Good

class GoodsForm(forms.ModelForm):
    class Meta:
        model = Good
        fields = ['name', 'price']