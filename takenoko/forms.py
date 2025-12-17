from django import forms
from django.core.exceptions import ValidationError
from .models import TakenokoUser

class TakenokoSignupForm(forms.ModelForm):
    password = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput,
        min_length=8,
        help_text="8文字以上"
    )

    class Meta:
        model = TakenokoUser
        fields = ["avatar", "nickname", "email", "student_id", "major", "grade", "password"]

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email.endswith("@tut.jp"):
            raise ValidationError("tut.jpドメインのメールアドレスのみ登録できます。")
        if TakenokoUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("このメールアドレスは既に登録されています。")
        return email

    def clean_student_id(self):
        sid = (self.cleaned_data.get("student_id") or "").strip()
        if not sid.isdigit():
            raise ValidationError("学籍番号は半角数字のみです。")
        if len(sid) < 4 or len(sid) > 20:
            raise ValidationError("学籍番号の長さが不正です。")
        if TakenokoUser.objects.filter(student_id=sid).exists():
            raise ValidationError("この学籍番号は既に登録されています。")
        return sid

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError("画像サイズは5MB以下にしてください。")
            content_type = getattr(avatar, "content_type", "")
            if not content_type.startswith("image/"):
                raise ValidationError("画像ファイルをアップロードしてください。")
        return avatar

    def save(self, commit=True):
        user = super().save(commit=False)
        raw_password = self.cleaned_data["password"]
        user.set_password(raw_password)  # ハッシュ化して保存
        if commit:
            user.save()
        return user