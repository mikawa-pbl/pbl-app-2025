from django import forms
from .models import Floor

class RoomSearchForm(forms.Form):
    room_number = forms.CharField(
        label='部屋番号', required=False,
        widget=forms.TextInput(attrs={'placeholder': '例: 3A-201'})
    )
    floor = forms.ModelChoiceField(
        label='フロア', required=False, queryset=Floor.objects.all(),
        empty_label='すべてのフロア'
    )
