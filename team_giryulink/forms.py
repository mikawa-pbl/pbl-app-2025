from django import forms
from django.core.exceptions import ValidationError
from .models import GiryulinkUser, validate_tut_email


class RegistrationForm(forms.Form):
    email = forms.EmailField(
        label='メールアドレス (@tut.jp)',
        validators=[validate_tut_email],
        widget=forms.EmailInput(attrs={
            'placeholder': 'your_name@tut.jp',
            'class': 'form-control'
        })
    )
    name = forms.CharField(
        label='表示名',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'お名前',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'パスワードを入力',
            'class': 'form-control'
        })
    )
    password_confirm = forms.CharField(
        label='パスワード確認',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'パスワードを再入力',
            'class': 'form-control'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if GiryulinkUser.objects.filter(email=email).exists():
            raise ValidationError('このメールアドレスは既に登録されています。')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError('パスワードが一致しません。')
        
        return cleaned_data
    
    def save(self):
        user = GiryulinkUser(
            email=self.cleaned_data['email'],
            name=self.cleaned_data.get('name', '')
        )
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='メールアドレス',
        widget=forms.EmailInput(attrs={
            'placeholder': 'your_name@tut.jp',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'パスワードを入力',
            'class': 'form-control'
        })
    )
