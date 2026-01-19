from django import forms
from django.core.exceptions import ValidationError
from .models import BookReview, SubjectReview, CourseOffering, GraphicsUser


class PasswordConfirmMixin:
    """
    パスワード確認フィールドのバリデーションを提供するミックスイン
    """
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise ValidationError("パスワードが一致しません。")

        return cleaned_data


class BookReviewForm(forms.ModelForm):
    """
    参考書レビュー入力フォーム
    """
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        initial=0,
        widget=forms.HiddenInput(attrs={'id': 'book-rating-value'}),
        label='おすすめ度',
        error_messages={
            'min_value': 'おすすめ度を選択してください（1〜5つ星）',
            'required': 'おすすめ度を選択してください',
        }
    )

    class Meta:
        model = BookReview
        fields = ['subject', 'isbn', 'review', 'rating']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例: データベース概論',
                'id': 'book-subject-input',
                'autocomplete': 'off'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例: 9784000000000',
                'maxlength': '50'
            }),
            'review': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'この参考書のレビューを書いてください',
                'rows': 5
            }),
        }
        labels = {
            'subject': '科目名',
            'isbn': 'ISBN',
            'review': 'レビュー',
        }

    def clean_isbn(self):
        """
        ISBNコードのバリデーション
        - ハイフンを除去
        - 正確に13桁であること
        - 数字のみであること
        """
        isbn = self.cleaned_data.get('isbn')

        # ISBNが空の場合はそのまま返す（オプション）
        if not isbn:
            return ''

        # ハイフンを除去
        isbn = isbn.replace('-', '')

        if len(isbn) != 13:
            raise forms.ValidationError('ISBNコードは13桁で入力してください。')

        if not isbn.isdigit():
            raise forms.ValidationError('ISBNコードは数字のみで入力してください。')

        return isbn


class SubjectReviewForm(forms.ModelForm):
    """
    科目レビュー入力フォーム
    """
    # course_offeringの代わりに科目名をテキスト入力
    subject_name = forms.CharField(
        max_length=200,
        label='科目名',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '科目名を入力してください',
            'autocomplete': 'off',
        }),
        required=False
    )

    # 年度選択フィールド
    year = forms.ChoiceField(
        label='年度',
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        required=False
    )

    # 開講学期選択フィールド
    semester = forms.ChoiceField(
        label='開講学期',
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        required=False
    )

    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        initial=0,
        widget=forms.HiddenInput(attrs={'id': 'subject-rating-value'}),
        label='おすすめ度',
        error_messages={
            'min_value': 'おすすめ度を選択してください（1〜5つ星）',
            'required': 'おすすめ度を選択してください',
        }
    )

    class Meta:
        model = SubjectReview
        fields = ['review', 'rating']
        widgets = {
            'review': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'この科目のレビューを書いてください（授業の難易度、内容、おすすめポイントなど）',
                'rows': 5
            }),
        }
        labels = {
            'review': 'レビュー',
        }


class SignupForm(PasswordConfirmMixin, forms.ModelForm):
    """
    サインアップフォーム
    """
    email_prefix = forms.CharField(
        label="メールアドレス",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例: s123456'}),
        help_text="@tut.jpは自動的に付加されます"
    )

    password = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
        help_text="8文字以上"
    )

    password_confirm = forms.CharField(
        label="パスワード（確認）",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
        help_text="確認のため再度入力してください"
    )

    class Meta:
        model = GraphicsUser
        fields = ['nickname', 'password']
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ニックネーム'}),
        }
        labels = {
            'nickname': 'ニックネーム',
        }

    def clean_email_prefix(self):
        email_prefix = (self.cleaned_data.get("email_prefix") or "").strip().lower()
        if not email_prefix:
            raise ValidationError("メールアドレスを入力してください。")

        # @が含まれている場合はエラー
        if "@" in email_prefix:
            raise ValidationError("@以前の部分のみを入力してください。")

        # 完全なメールアドレスを生成
        email = f"{email_prefix}@tut.jp"

        # 既存チェック
        if GraphicsUser.objects.using('graphics').filter(email__iexact=email).exists():
            raise ValidationError("このメールアドレスは既に登録されています。")

        return email_prefix

    def save(self, commit=True):
        user = super().save(commit=False)
        raw_password = self.cleaned_data["password"]
        email_prefix = self.cleaned_data["email_prefix"]

        # 完全なメールアドレスを設定
        user.email = f"{email_prefix}@tut.jp"
        user.set_password(raw_password)

        if commit:
            user.save(using='graphics')
        return user


class LoginForm(forms.Form):
    """
    ログインフォーム
    """
    email_prefix = forms.CharField(
        label="メールアドレス",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例: s123456'}),
        help_text="@tut.jpは自動的に付加されます"
    )
    password = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class PasswordResetRequestForm(forms.Form):
    """
    パスワードリセット申請フォーム
    """
    email_prefix = forms.CharField(
        label="メールアドレス",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例: s123456'}),
        help_text="@tut.jpは自動的に付加されます"
    )


class PasswordResetForm(PasswordConfirmMixin, forms.Form):
    """
    パスワードリセットフォーム
    """
    password = forms.CharField(
        label="新しいパスワード",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
        help_text="8文字以上"
    )

    password_confirm = forms.CharField(
        label="新しいパスワード（確認）",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
        help_text="確認のため再度入力してください"
    )


class BookReviewEditForm(forms.ModelForm):
    """
    参考書レビュー編集フォーム（レビュー内容と評価を編集可能）
    """
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput(attrs={'id': 'edit-book-rating-value'}),
        label='おすすめ度',
        error_messages={
            'min_value': 'おすすめ度を選択してください（1〜5つ星）',
            'required': 'おすすめ度を選択してください',
        }
    )

    class Meta:
        model = BookReview
        fields = ['review', 'rating']
        widgets = {
            'review': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'この参考書のレビューを書いてください',
                'rows': 5
            }),
        }
        labels = {
            'review': 'レビュー内容',
        }


class SubjectReviewEditForm(forms.ModelForm):
    """
    科目レビュー編集フォーム（レビュー内容と評価を編集可能）
    """
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput(attrs={'id': 'edit-subject-rating-value'}),
        label='おすすめ度',
        error_messages={
            'min_value': 'おすすめ度を選択してください（1〜5つ星）',
            'required': 'おすすめ度を選択してください',
        }
    )

    class Meta:
        model = SubjectReview
        fields = ['review', 'rating']
        widgets = {
            'review': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'この科目のレビューを書いてください',
                'rows': 5
            }),
        }
        labels = {
            'review': 'レビュー内容',
        }
