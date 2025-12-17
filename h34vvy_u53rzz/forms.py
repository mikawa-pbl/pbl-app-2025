from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser

from .models import Entry


class SignupForm(forms.Form):
    username = forms.CharField(
        label="ユーザー名",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40",
                "placeholder": "アプリ内で使うユーザー名",
                "autocomplete": "username",
            }
        ),
    )
    password1 = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40",
                "placeholder": "パスワード",
                "autocomplete": "new-password",
            }
        ),
    )
    password2 = forms.CharField(
        label="パスワード（確認）",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40",
                "placeholder": "もう一度入力してください",
                "autocomplete": "new-password",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "パスワードが一致しません。")
        return cleaned_data


class NamespacedLoginForm(forms.Form):
    username = forms.CharField(
        label="ユーザー名",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40",
                "placeholder": "アプリ内のユーザー名",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40",
                "placeholder": "パスワード",
                "autocomplete": "current-password",
            }
        ),
    )

    error_messages = {
        "invalid_login": "ユーザー名またはパスワードが正しくありません。",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        if username and password:
            user = authenticate(self.request, username=username, password=password)
            if not user.is_authenticated:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )
            self.user_cache = user
        return cleaned_data

    def get_user(self):
        return self.user_cache


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ["comment"]
        labels = {
            "comment": "コメント",
        }
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40",
                    "placeholder": "コメントを書いて送信すると、下に積み上がっていきます",
                }
            ),
        }
