from django import forms
from .models import StatusReport
from django.utils import timezone
import pytz 

class StatusReportForm(forms.ModelForm):
    
    floor = forms.ChoiceField(
        choices=StatusReport.FLOOR_CHOICES,
        label='階',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = StatusReport
        fields = ['symptom', 'floor', 'description', 'timestamp', 'latitude', 'longitude']
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            
            'timestamp': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timestamp'].required = False
        tokyo_tz = pytz.timezone("Asia/Tokyo")
        self.fields['timestamp'].initial = timezone.localtime(timezone.now()).astimezone(tokyo_tz).strftime('%Y-%m-%dT%H:%M')
        self.fields['floor'].initial = 1

    def clean_timestamp(self):
        timestamp = self.cleaned_data.get('timestamp')
        naive_datetime = timestamp.replace(tzinfo=None)
        jst_tz = pytz.timezone('Asia/Tokyo')
        aware_datetime_jst = jst_tz.localize(naive_datetime)
        return aware_datetime_jst
