from django import forms
from .models import Good

class GoodsForm(forms.ModelForm):
    class Meta:
        model = Good
        # include image and description so uploaded files and text are saved
        fields = ['name', 'price', 'image', 'description']