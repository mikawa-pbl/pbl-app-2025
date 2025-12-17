from django import forms
from django.core.exceptions import ValidationError
from .models import TakenokoUser, Item, ItemImage, TargetGrade, Tag

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


class ItemCreateForm(forms.ModelForm):
    grades = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="対象学年"
    )
    tags = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="タグ/カテゴリ"
    )

    class Meta:
        model = Item
        fields = ['name', 'price', 'description', 'condition']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 対象学年: DBが空なら GRADE_CHOICES を使用
        db_grade_choices = list(TargetGrade.objects.values_list('code', 'display_name'))
        self.fields['grades'].choices = db_grade_choices if db_grade_choices else list(TargetGrade.GRADE_CHOICES)

        # タグの選択肢（任意）: DBの内容をそのまま使用
        self.fields['tags'].choices = list(Tag.objects.values_list('name', 'display_name'))

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            raise ValidationError("価格を入力してください。")
        if price > 99999:
            raise ValidationError("価格は99,999円以下にしてください。")
        if price < 0:
            raise ValidationError("価格は0円以上にしてください。")
        return price

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        if len(description) > 300:
            raise ValidationError("商品詳細は300文字以内で入力してください。")
        return description

    def validate_images(self, files):
        """画像ファイルのバリデーション（viewsから呼び出される）"""
        errors = []
        
        if len(files) > 5:
            errors.append("画像は最大5枚までです。")
        
        for image in files:
            if image.size > 5 * 1024 * 1024:
                errors.append(f"{image.name}: 画像サイズは5MB以下にしてください。")
            
            content_type = getattr(image, 'content_type', '')
            if not content_type.startswith('image/'):
                errors.append(f"{image.name}: 画像ファイルのみアップロード可能です。")
        
        return errors