from django import forms
from .models import StatusReport
from django.utils import timezone
import pytz # Re-introduce pytz

class StatusReportForm(forms.ModelForm):
    
    class Meta:
        model = StatusReport

        fields = ['symptom', 'location', 'description', 'timestamp']
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            
            'timestamp': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                },
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timestamp'].required = False
        if not self.instance.pk: # Only set initial for new objects
            tokyo_tz = pytz.timezone("Asia/Tokyo")
            # Get current UTC time, convert to JST, then format
            self.fields['timestamp'].initial = timezone.localtime(timezone.now()).astimezone(tokyo_tz).strftime('%Y-%m-%dT%H:%M')

    def clean_timestamp(self):
        timestamp = self.cleaned_data.get('timestamp')
        if timestamp:
            # timestamp is an aware datetime in UTC, but the user *meant* it to be JST.
            # So, we treat the time part as if it were JST.
            
            # 1. Get the naive datetime (stripping the UTC timezone)
            naive_datetime = timestamp.replace(tzinfo=None)
            
            # 2. Make it aware in JST
            jst_tz = pytz.timezone('Asia/Tokyo')
            aware_datetime_jst = jst_tz.localize(naive_datetime)
            
            # 3. The form will then save this, and Django will convert to UTC for DB storage
            return aware_datetime_jst
        return timestamp