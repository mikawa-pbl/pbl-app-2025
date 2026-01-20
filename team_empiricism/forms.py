from django import forms
from .models import ExperimentPost

class ExperimentPostForm(forms.ModelForm):
    """
    実験投稿用のフォーム
    """
    class Meta:
        model = ExperimentPost
        fields = [
            'title', 'description', 'reward', 'duration',
            'start_date', 'end_date', 'location', 'requirements',
            'capacity', 'organizer_name', 'laboratory', 'application_url',
            'edit_password', 'status'
        ]
        # 'application_url': Google Forms 機能
        widgets = {
            # HTML5の日付選択ピッカーを使用するための設定
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 3}),
            # パスワード入力を見えないように設定(V3)
            'edit_password': forms.PasswordInput(attrs={'placeholder': '4桁の数字', 'pattern': '[0-9]{4}', 'inputmode': 'numeric'}),
        }
        # 追加(V3)
        labels = {
            'edit_password': '編集・削除用パスワード（4桁数字）'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap用のクラスを適用
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class PasswordConfirmForm(forms.Form):
    """
    編集・削除時のパスワード確認用フォーム(V3)
    """
    password = forms.CharField(
        label='パスワード',
        max_length=4,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': '投稿時に設定した4桁の数字',
            'pattern': '[0-9]{4}',
            'inputmode': 'numeric'
        })
    )