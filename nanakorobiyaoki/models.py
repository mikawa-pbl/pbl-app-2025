from django.db import models

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class MyPage(models.Model):
    # 性別の選択肢
    GENDER_CHOICES = [
        ('男性', '男性'),
        ('女性', '女性'),
        ('その他', 'その他'),
        ('回答しない', '回答しない'),
    ]



    GRADE_CHOICES = [
        ('B1','B1'),
        ('B2','B2'),
        ('B3','B3'),
        ('B4','B4'),
        ('M1','M1'),
        ('M2','M2'),
    ]

    DEPARTMENT_CHOICES = [
        ('1系','1系'),
        ('2系','2系'),
        ('3系','3系'),
        ('4系','4系'),
        ('5系','5系'),
    ]

    # 基本情報
    name = models.CharField(max_length=100, verbose_name="名前(フルネーム推奨)")
    icon = models.ImageField(upload_to='icons/', blank=True, null=True, verbose_name="アイコン")
    user_id = models.CharField(max_length=100, unique=True, verbose_name="学籍番号(数字6桁)")
    email = models.EmailField(max_length=100, verbose_name="メールアドレス")
    password = models.CharField(max_length=100, verbose_name="パスワード")
    
    # プロフィール情報
    grade = models.CharField(
        max_length=50, 
        choices=GRADE_CHOICES, # プルダウンにする
        verbose_name="学年",
        null=True,
    )
    
    department = models.CharField(
        max_length=50, 
        choices=DEPARTMENT_CHOICES, # プルダウンにする
        verbose_name="学科",
        null=True,
    )

    gender = models.CharField(
        max_length=50, 
        choices=GENDER_CHOICES, # プルダウンにする
        verbose_name="性別",
        default='回答しない' 
    )
    club = models.CharField(max_length=100, blank=True, null=True, verbose_name="所属サークル")
    one_word = models.TextField(blank=True, null=True, verbose_name="一言")
    github_account = models.CharField(max_length=100, blank=True, null=True, verbose_name="githubアカウント")
    hobby = models.CharField(max_length=200, blank=True, null=True, verbose_name="趣味")
    birthplace = models.CharField(max_length=100, blank=True, null=True, verbose_name="出身")
    birth_date = models.DateField(verbose_name="誕生日", null=True, blank=True)

    def __str__(self):
        return self.name # ページの名前がその人の名前になる

class Community(models.Model):
    name = models.CharField(max_length=100, verbose_name="コミュニティ名")
    description = models.TextField(verbose_name="説明", blank=True, null=True)
    image = models.ImageField(upload_to='communities/', blank=True, null=True, verbose_name="画像")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    members = models.ManyToManyField(MyPage, related_name='communities', verbose_name="参加メンバー")

    def __str__(self):
        return self.name

class Post(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts', verbose_name="コミュニティ")
    author = models.ForeignKey(MyPage, on_delete=models.CASCADE, related_name='posts', verbose_name="投稿者")
    content = models.TextField(verbose_name="内容")
    image = models.ImageField(upload_to='posts/', blank=True, null=True, verbose_name="画像")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="投稿日時")

    def __str__(self):
        return f"{self.community.name} - {self.author.name} ({self.created_at})"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="投稿")
    author = models.ForeignKey(MyPage, on_delete=models.CASCADE, related_name='comments', verbose_name="コメント者")
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="投稿日時")

    def __str__(self):
        return f"Comment by {self.author.name}"
