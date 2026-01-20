# shiokara/forms.py
from django import forms
from .models import Person

DEGREE_CHOICES = [
    ("B", "学部(B)"),
    ("M", "修士(M)"),
    ("D", "博士(D)"),
]

# 年は JavaScript で絞るので、ひとまず 1〜4 年を全部定義しておく
YEAR_CHOICES = [
    ("1", "1年"),
    ("2", "2年"),
    ("3", "3年"),
    ("4", "4年"),
]

DEPARTMENT_CHOICES = [
    ("機械工学(1系)", "機械工学(1系)"),
    ("電気・電子情報工学(2系)", "電気・電子情報工学(2系)"),
    ("情報・知能工学(3系)", "情報・知能工学(3系)"),
    ("応用化学・生命工学(4系)", "応用化学・生命工学(4系)"),
    ("建築・都市システム学(5系)", "建築・都市システム学(5系)"),
]

LAB_CHOICES = [
    # 1系
    ("機械・システムデザインコース", "1系: 機械・システムデザインコース"),
    ("材料・生産加工コース", "1系: 材料・生産加工コース"),
    ("システム制御・ロボットコース", "1系: システム制御・ロボットコース"),
    ("環境・エネルギーコース", "1系: 環境・エネルギーコース"),
    # 2系
    ("材料エレクトロニクスコース", "2系: 材料エレクトロニクスコース"),
    ("機能電気システムコース", "2系: 機能電気システムコース"),
    ("集積電子システムコース", "2系: 集積電子システムコース"),
    ("情報通信システムコース", "2系: 情報通信システムコース"),
    # 3系
    ("計算機数理科学分野", "3系: 計算機数理科学分野"),
    ("データ情報学分野", "3系: データ情報学分野"),
    ("ヒューマン・ブレイン情報学分野", "3系: ヒューマン・ブレイン情報学分野"),
    ("メディア・ロボット情報学分野", "3系: メディア・ロボット情報学分野"),
    # 4系
    ("分子制御化学分野", "4系: 分子制御化学分野"),
    ("分子生物化学分野", "4系: 分子生物化学分野"),
    ("分子機能化学分野", "4系: 分子機能化学分野"),
    # 5系
    ("建築・都市デザイン学分野", "5系: 建築・都市デザイン学分野"),
    ("都市・地域マネジメント学分野", "5系: 都市・地域マネジメント学分野"),
]


class PersonLoginForm(forms.Form):
    student_id = forms.CharField(
        label="学籍番号",
        max_length=20,
    )
    degree = forms.ChoiceField(
        label="課程",
        choices=DEGREE_CHOICES,
        widget=forms.RadioSelect,
    )
    year = forms.ChoiceField(
        label="学年",
        choices=YEAR_CHOICES,
    )
    department = forms.ChoiceField(
        label="学科・専攻",
        choices=DEPARTMENT_CHOICES,
    )
    lab_field = forms.ChoiceField(
        label="研究分野",
        choices=LAB_CHOICES,
    )
    password = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput,
    )
    name = forms.CharField(
        label="名前",
        max_length=50,
    )
