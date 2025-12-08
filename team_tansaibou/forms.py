from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Store


class StoreSignUpForm(UserCreationForm):
    """店舗登録フォーム（店舗+ユーザー同時作成）"""
    store_name = forms.CharField(
        label='店舗名',
        max_length=100,
        help_text='模擬店の名前を入力してください',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '例: たこ焼き屋さん'
        })
    )
    description = forms.CharField(
        label='店舗の説明',
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 3,
            'placeholder': '店舗の説明（任意）'
        }),
        required=False
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-input'
        self.fields['username'].widget.attrs['placeholder'] = 'ログイン用ID'
        self.fields['password1'].widget.attrs['placeholder'] = 'パスワード'
        self.fields['password2'].widget.attrs['placeholder'] = 'パスワード（確認）'

    def save(self, commit=True, using='team_tansaibou'):
        user = super().save(commit=commit)
        if commit:
            Store.objects.using(using).create(
                user_id=user.id,
                name=self.cleaned_data['store_name'],
                description=self.cleaned_data.get('description', '')
            )
        return user


class StoreLoginForm(AuthenticationForm):
    """ログインフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'ログインID'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'パスワード'
        })
