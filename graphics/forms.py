from django import forms
from .models import BookReview, SubjectReview, CourseOffering


class BookReviewForm(forms.ModelForm):
    """
    参考書レビュー入力フォーム
    """
    rating = forms.IntegerField(
        min_value=0,
        max_value=5,
        initial=0,
        widget=forms.HiddenInput(attrs={'id': 'book-rating-value'}),
        label='おすすめ度'
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
        min_value=0,
        max_value=5,
        initial=0,
        widget=forms.HiddenInput(attrs={'id': 'subject-rating-value'}),
        label='おすすめ度'
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
