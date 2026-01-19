from django import forms
from .models import Good, SOSMessage


class GoodsForm(forms.ModelForm):
    # file input is handled in the view and saved to app templates/images
    image = forms.FileField(required=False)

    class Meta:
        model = Good
        fields = ['name', 'description', 'price', 'original_price']


class SOSMessageForm(forms.ModelForm):
    class Meta:
        model = SOSMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400'}),
        }
