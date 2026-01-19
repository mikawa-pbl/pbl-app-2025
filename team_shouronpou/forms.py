from django import forms
from .models import Post, Account
import json

class PostForm(forms.ModelForm):
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
            'condition_nationality', 'condition_gender',
            'target_age', 'health_notes', 'free_notes',
            'message_for_applicants'  # 追加
        ]
        widgets = {
            'recruitment_end_date': forms.DateInput(attrs={'type': 'date'}),
            'condition_nationality': forms.TextInput(attrs={'placeholder': '例: 指定なし、日本国籍のみ など'}),
            'target_age': forms.TextInput(attrs={'placeholder': '例: 20代、18歳以上 など'}),
            'available_slots': forms.HiddenInput(),
            'content': forms.Textarea(attrs={'rows': 4}),
            'health_notes': forms.Textarea(attrs={'rows': 2}),
            'free_notes': forms.Textarea(attrs={'rows': 2}),
            # 追加
            'message_for_applicants': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': '例: 応募ありがとうございます。詳細は example@mail.com までご連絡ください。'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if self.instance.max_participants is None:
                self.initial['participants_selector'] = 'unlimited'
            elif 1 <= self.instance.max_participants <= 10:
                self.initial['participants_selector'] = str(self.instance.max_participants)
            else:
                self.initial['participants_selector'] = 'custom'
                self.initial['custom_participants'] = self.instance.max_participants

    def clean(self):
        cleaned_data = super().clean()
        selector = cleaned_data.get('participants_selector')
        custom_val = cleaned_data.get('custom_participants')

        if selector == 'unlimited':
            cleaned_data['max_participants'] = None
        elif selector == 'custom':
            if not custom_val:
                self.add_error('custom_participants', '人数を入力してください。')
            cleaned_data['max_participants'] = custom_val
        else:
            cleaned_data['max_participants'] = int(selector)
        return cleaned_data

class AccountForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="パスワード")
    class Meta:
        model = Account
        fields = ['username', 'password']

class LoginForm(forms.Form):
    username = forms.CharField(label="ユーザー名")
    password = forms.CharField(widget=forms.PasswordInput, label="パスワード")

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
            except:
                return []
        return data