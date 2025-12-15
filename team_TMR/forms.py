from django import forms
from .models import Profile, Roadmap, ES, InvitationCode

DEFAULT_CODES = ['TMR_DEFAULT_2025', 'PBL_FIGHT_ON']

class InvitationCodeForm(forms.Form):
    invitation_code = forms.CharField(label="招待コード", max_length=50)

    def clean_invitation_code(self):
        code_str = self.cleaned_data.get('invitation_code')
        if code_str in DEFAULT_CODES:
            return code_str
        try:
            code_obj = InvitationCode.objects.get(code=code_str, used=False)
        except InvitationCode.DoesNotExist:
            raise forms.ValidationError("有効な招待コードではありません。")
        return code_str

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname', 'affiliation', 'contact']

class RoadmapForm(forms.ModelForm):
    class Meta:
        model = Roadmap
        fields = ['title', 'start_date', 'end_date', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class ESForm(forms.ModelForm):
    class Meta:
        model = ES
        fields = ['company', 'question', 'answer']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }