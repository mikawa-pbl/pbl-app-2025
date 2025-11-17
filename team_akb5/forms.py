from django import forms
from .models import StatusReport

class StatusReportForm(forms.ModelForm):
    
    class Meta:
        model = StatusReport

        fields = ['symptom', 'location', 'description', 'timestamp']
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            
            'timestamp': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'placeholder': '空欄で現在時刻',
                },
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timestamp'].required = False