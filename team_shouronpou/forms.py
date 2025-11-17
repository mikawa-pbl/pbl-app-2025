from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    # 1. 選択肢の定義 (1〜10名、無制限、カスタム)
    SELECTION_CHOICES = [
        (str(i), f'{i}名') for i in range(1, 11)
    ] + [
        ('unlimited', '無制限'),
        ('custom', '自身で入力（1名以上）'),
    ]

    # 2. UI用のフィールド定義（DBには保存されない一時的なフィールド）
    participants_selector = forms.ChoiceField(
        choices=SELECTION_CHOICES,
        label="募集人数",
        required=False
    )
    custom_participants = forms.IntegerField(
        label="人数を入力",
        min_value=1, # フォームレベルでも1以上を強制
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': '例: 15', 'style': 'display:none;'}) # 初期状態は非表示
    )

    class Meta:
        model = Post
        fields = [
            'title', 
            'content', 
            'recruitment_start_date', 
            'recruitment_end_date', 
            'condition_nationality',
            'condition_gender',
            'condition_has_disease',
        ]
        widgets = {
            'recruitment_start_date': forms.DateInput(attrs={'type': 'date'}),
            'recruitment_end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 編集時（インスタンスがある場合）の初期値設定
        if self.instance.pk:
            current_max = self.instance.max_participants

            if current_max is None:
                # DBがNoneなら「無制限」を選択状態に
                self.fields['participants_selector'].initial = 'unlimited'
            elif 1 <= current_max <= 10:
                # 1〜10ならその数字を選択状態に
                self.fields['participants_selector'].initial = str(current_max)
            else:
                # それ以外（11以上など）なら「自身で入力」を選択し、数値をセット
                self.fields['participants_selector'].initial = 'custom'
                self.fields['custom_participants'].initial = current_max
                # カスタム入力欄を表示状態にするスタイル上書き
                self.fields['custom_participants'].widget.attrs.update({'style': 'display:block;'})

    def clean(self):
        """
        フォームの送信時に実行される検証・データ加工処理
        """
        cleaned_data = super().clean()
        selector = cleaned_data.get('participants_selector')
        custom_val = cleaned_data.get('custom_participants')

        # 選択肢に応じて max_participants (モデルのフィールド) に値をセット
        if selector == 'unlimited':
            self.instance.max_participants = None
        elif selector == 'custom':
            if not custom_val:
                self.add_error('custom_participants', '人数を入力してください。')
            else:
                self.instance.max_participants = custom_val
        elif selector:
            # 1〜10が選択された場合
            self.instance.max_participants = int(selector)

        return cleaned_data
