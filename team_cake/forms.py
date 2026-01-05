from django import forms
from .models import Good


class GoodsForm(forms.ModelForm):
    # file input is handled in the view and saved to app templates/images
    image = forms.FileField(required=False)

    class Meta:
        model = Good
        fields = ['name', 'description', 'price', 'original_price']