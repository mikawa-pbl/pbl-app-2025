from django.db import models

# Create your models here.
class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

#class Paper(models.Model):
#    title = models.CharField(max_length=200)
#    author = models.CharField(max_length=200)
#    year = models.IntegerField()
#    booktitle = models.CharField(max_length=200)
#    url = models.URLField()
#    doi = models.CharField(max_length=100)
#
#    def __str__(self):
#        return f"{self.title} {self.author} {self.year}"

from django.core.validators import FileExtensionValidator

class Paper(models.Model):
    # 通し番号: Django が自動で primary key を付けてくれるが、
    # 明示的に書いてもOK（無くても動きます）
    id = models.AutoField('通し番号', primary_key=True)

    # *論文題目
    title = models.CharField('論文題目', max_length=300)

    # *論文著者
    author = models.CharField('論文著者', max_length=300)

    # *掲載誌名
    booktitle = models.CharField('掲載誌名', max_length=300)

    # *年
    year = models.IntegerField('年')

    # *DOI
    doi = models.CharField('DOI', max_length=100)

    # *URL
    url = models.URLField('URL', max_length=500)

    # *登録者
    submitter = models.CharField('登録者', max_length=100)

    # *登録時刻（自動保存・編集不可）
    submit_time = models.DateTimeField('登録時刻', auto_now_add=True, editable=False)

    # キーワード（任意）
    keywords = models.CharField('キーワード', max_length=300, blank=True)

    # *どんな論文か
    imp_overview = models.TextField('どんな論文か')

    # *先行研究との比較
    imp_comparison = models.TextField('先行研究との比較')

    # *技術や手法の中心的アイデア
    imp_idea = models.TextField('技術や手法の中心的アイデア')

    # *有効性の検証方法と結果
    imp_usefulness = models.TextField('有効性の検証方法と結果')

    # *議論（利点，欠点，制限）
    imp_discussion = models.TextField('議論（利点，欠点，制限）')

    # 自身の研究との関連性（任意）
    imp_relation = models.TextField('自身の研究との関連性', blank=True)

    # その他（任意）
    note = models.TextField('その他', blank=True)

    # 論文ファイル: PDF
    paper_file = models.FileField(
        '論文ファイル',
        upload_to='paper_files/',
        blank=True,
        validators=[FileExtensionValidator(['pdf'])]
    )

    # 輪講スライド: pptx or pdf
    rc_slide = models.FileField(
        '輪講スライド',
        upload_to='rc_slides/',
        blank=True,
        validators=[FileExtensionValidator(['ppt', 'pptx', 'pdf'])]
    )

    # 画像ファイル: png, jpg, jpeg, pdf
    paper_figure = models.FileField(
        '画像ファイル',
        upload_to='paper_figures/',
        blank=True,
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'pdf'])]
    )

    def __str__(self):
        return f'{self.title} ({self.year})'
