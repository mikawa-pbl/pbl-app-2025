from django import forms
from .models import Post
import json

class PostForm(forms.ModelForm):
    # --- 人数選択肢 ---
    SELECTION_CHOICES = [
        (str(i), f'{i}名') for i in range(1, 11)
    ] + [
        ('unlimited', '無制限'),
        ('custom', '自身で入力（1名以上）'),
    ]

    # --- フォーム独自のフィールド定義 ---
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

    # 条件ON/OFF用のチェックボックス
    enable_nationality = forms.BooleanField(label="国籍条件を設定する", required=False)
    enable_gender = forms.BooleanField(label="性別条件を設定する", required=False)
    enable_disease = forms.BooleanField(label="持病条件を設定する", required=False)

    class Meta:
        model = Post
        fields = [
            'title', 
            'content', 
            'recruitment_end_date',
            'max_participants',
            'available_slots', 
            'condition_nationality',
            'condition_gender',
            'condition_has_disease',
        ]
        widgets = {
            'recruitment_end_date': forms.DateInput(attrs={'type': 'date'}),
            'condition_nationality': forms.RadioSelect(),
            'condition_gender': forms.RadioSelect(),
            'condition_has_disease': forms.RadioSelect(),
            'available_slots': forms.HiddenInput(), 
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': '募集内容（100文字以内）',
                'maxlength': '100',  # <--- これを追加するだけで、ブラウザ上で入力制限がかかります
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # --- 編集画面を開いた時の初期値設定 ---
        if self.instance.pk:
            # 1. 人数設定の復元
            current_max = self.instance.max_participants
            if current_max is None:
                self.fields['participants_selector'].initial = 'unlimited'
            elif 1 <= current_max <= 10:
                self.fields['participants_selector'].initial = str(current_max)
            else:
                self.fields['participants_selector'].initial = 'custom'
                self.fields['custom_participants'].initial = current_max
                self.fields['custom_participants'].widget.attrs.update({'style': 'display:inline-block;'})
            
            # 2. 条件チェックボックスの復元
            if self.instance.condition_nationality:
                self.fields['enable_nationality'].initial = True
            if self.instance.condition_gender:
                self.fields['enable_gender'].initial = True
            if self.instance.condition_has_disease:
                self.fields['enable_disease'].initial = True

            # 3. 時間割データの復元
            if self.instance.available_slots:
                self.initial['available_slots'] = json.dumps(self.instance.available_slots)

    def clean_available_slots(self):
        """
        保存時の処理: HTMLから送られてきたJSON文字列をPythonリストに戻す
        """
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
        
        # --- 人数ロジック ---
        selector = cleaned_data.get('participants_selector')
        custom_val = cleaned_data.get('custom_participants')
        
        # 保存する値をここで決定する
        final_max = None # デフォルトは無制限(None)

        if selector == 'custom':
            if not custom_val:
                self.add_error('custom_participants', '人数を入力してください。')
            else:
                final_max = custom_val
        elif selector == 'unlimited':
            final_max = None
        elif selector:
            final_max = int(selector)

        # ★重要修正★ 
        # self.instance.max_participants = ... ではなく
        # cleaned_data['max_participants'] = ... に入れることで、Djangoの保存処理に正しく渡す
        cleaned_data['max_participants'] = final_max


        # --- 条件ON/OFFロジック ---
        # こちらも念のため cleaned_data を書き換える方式に統一
        if not cleaned_data.get('enable_nationality'):
            cleaned_data['condition_nationality'] = None
        if not cleaned_data.get('enable_gender'):
            cleaned_data['condition_gender'] = None
        if not cleaned_data.get('enable_disease'):
            cleaned_data['condition_has_disease'] = None
        
        return cleaned_data