from django import forms
from django.contrib.auth import authenticate

from .models import Entry


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
