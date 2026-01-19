from django import forms
from .models import Post, Account
import json

class PostForm(forms.ModelForm):
    # --- 人数選択肢 ---
    SELECTION_CHOICES = [
        (str(i), f'{i}名') for i in range(1, 11)
    ] + [
        ('unlimited', '無制限'),
        ('custom', '自身で入力（1名以上）'),
    ]

    participants_selector = forms.ChoiceField(
        choices=SELECTION_CHOICES,
        label="募集人数",
        required=False,
        initial='unlimited'
    )

    custom_participants = forms.IntegerField(
        label="人数を入力",
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': '例: 15', 'style': 'display:none;'})
    )

    class Meta:
        model = Post
        fields = [
            'title', 
            'department', 'laboratory', 'reward', 'duration',
            'content', 'recruitment_end_date',
            'max_participants', 'available_slots', 
            
            # 条件フィールド
            'condition_nationality', 'condition_gender',
            
            # 任意項目
            'target_age', 'health_notes', 'free_notes', 
        ]
        widgets = {
            'recruitment_end_date': forms.DateInput(attrs={'type': 'date'}),
            
            # 国籍はテキスト入力
            'condition_nationality': forms.TextInput(attrs={'placeholder': '例: 指定なし、日本国籍のみ など'}),
            
            # 性別はラジオボタン（必須・デフォルト指定なし）
            'condition_gender': forms.RadioSelect(),
            
            'available_slots': forms.HiddenInput(), 
            
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': '募集内容（100文字以内）',
                'maxlength': '100',
            }),
            'department': forms.TextInput(attrs={'placeholder': '例: 機械工学系'}),
            'laboratory': forms.TextInput(attrs={'placeholder': '例: 〇〇研究室'}),
            'reward': forms.TextInput(attrs={'placeholder': '例: Amazonギフト券 1000円分'}),
            'duration': forms.NumberInput(attrs={'placeholder': '例: 60'}),
            'target_age': forms.TextInput(attrs={'placeholder': '例: 20歳以上、学生限定など'}),
            'health_notes': forms.Textarea(attrs={'rows': 3, 'placeholder': '光の点滅があります、など'}),
            'free_notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'その他特記事項があれば'}),
        }
        labels = {
            'duration': '実験所要時間（分）',
            'health_notes': '健康面で配慮すべき事項（任意）',
            'free_notes': '自由項目（任意）',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 編集時の初期値設定
        if self.instance.pk:
            current_max = self.instance.max_participants
            if current_max is None:
                self.fields['participants_selector'].initial = 'unlimited'
            elif 1 <= current_max <= 10:
                self.fields['participants_selector'].initial = str(current_max)
            else:
                self.fields['participants_selector'].initial = 'custom'
                self.fields['custom_participants'].initial = current_max
                self.fields['custom_participants'].widget.attrs.update({'style': 'display:inline-block;'})
            
            # 時間割データの復元
            if self.instance.available_slots:
                self.initial['available_slots'] = json.dumps(self.instance.available_slots)

    def clean_available_slots(self):
        data = self.cleaned_data.get('available_slots')
        if isinstance(data, str):
            try:
                if not data: return []
                return json.loads(data)
            except json.JSONDecodeError:
                return []
        return data

    def clean(self):
        cleaned_data = super().clean()
        
        # 人数入力の制御
        selector = cleaned_data.get('participants_selector')
        custom_val = cleaned_data.get('custom_participants')
        final_max = None

        if selector == 'custom':
            if not custom_val:
                self.add_error('custom_participants', '人数を入力してください。')
            else:
                final_max = custom_val
        elif selector == 'unlimited':
            final_max = None
        elif selector:
            final_max = int(selector)

        cleaned_data['max_participants'] = final_max
        
        # ★重要: ここにあった「enable_gender」等のif文は全て削除しました。
        # データはそのまま保存されます。

        return cleaned_data


# 新規登録用フォーム
class AccountForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="パスワード")
    
    class Meta:
        model = Account
        fields = ['username', 'password']

# ログイン用フォーム
class LoginForm(forms.Form):
    username = forms.CharField(label="ユーザー名")
    password = forms.CharField(widget=forms.PasswordInput, label="パスワード")

# プロフィール編集用フォーム
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'affiliation', 'age', 'gender', 'nationality',
            'desired_max_time', 'available_slots'
        ]
        labels = {
            'affiliation': '所属（学部・研究室など）',
            'desired_max_time': '許容する実験時間（分）',
            'nationality': '国籍',
        }
        widgets = {
            'desired_max_time': forms.NumberInput(attrs={'placeholder': '例: 60'}),
            'nationality': forms.TextInput(attrs={'placeholder': '例: 日本'}),
            'gender': forms.RadioSelect(),
            'available_slots': forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.available_slots:
            self.initial['available_slots'] = json.dumps(self.instance.available_slots)

    def clean_available_slots(self):
        data = self.cleaned_data.get('available_slots')
        if isinstance(data, str):
            try:
                if not data: return []
                return json.loads(data)
            except json.JSONDecodeError:
                return []
        return data