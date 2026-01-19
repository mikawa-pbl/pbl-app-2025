# Generated manually for sample data

from django.db import migrations
from datetime import datetime, timedelta


def add_sample_data(apps, schema_editor):
    Account = apps.get_model('team_UD', 'Account')
    Company = apps.get_model('team_UD', 'Company')
    Memo = apps.get_model('team_UD', 'Memo')
    QuestionAnswer = apps.get_model('team_UD', 'QuestionAnswer')
    
    db_alias = schema_editor.connection.alias
    
    # アカウント1を取得または作成
    account, _ = Account.objects.using(db_alias).get_or_create(
        id=1,
        defaults={
            'username': 'testuser',
            'password': 'test123'
        }
    )
    
    # 会社データを作成
    companies_data = [
        '株式会社サイバーエージェント',
        '楽天グループ株式会社',
        'LINE株式会社',
        '株式会社メルカリ',
        'ヤフー株式会社'
    ]
    
    companies = []
    for company_name in companies_data:
        company, _ = Company.objects.using(db_alias).get_or_create(
            name=company_name
        )
        companies.append(company)
    
    # 今日の日付を基準に
    today = datetime.now().date()
    
    # 過去のメモ（面接質問付き）を作成
    past_memos_data = [
        {
            'company': companies[0],
            'date': today - timedelta(days=15),
            'interview_stage': '一次面接',
            'interview_date': today - timedelta(days=15),
            'interview_questions': '''志望動機を教えてください
学生時代に最も力を入れたことは何ですか？
チームで困難を乗り越えた経験について教えてください
当社のサービスで改善すべき点はありますか？''',
            'content': '雰囲気は和やかでした。技術的な質問は少なめで、人物重視の印象。',
            'title': '一次面接メモ'
        },
        {
            'company': companies[0],
            'date': today - timedelta(days=8),
            'interview_stage': '二次面接',
            'interview_date': today - timedelta(days=8),
            'interview_questions': '''あなたの強みと弱みを教えてください
5年後、どのようなエンジニアになっていたいですか？
技術的な課題に直面したとき、どう対応しますか？
最近気になっている技術トレンドは何ですか？''',
            'content': '技術面接。コーディングテストもありました。',
            'title': '二次面接メモ'
        },
        {
            'company': companies[1],
            'date': today - timedelta(days=20),
            'interview_stage': '一次面接',
            'interview_date': today - timedelta(days=20),
            'interview_questions': '''自己紹介をお願いします
なぜ楽天を志望しているのですか？
グローバルな環境で働くことについてどう思いますか？
失敗から学んだ経験を教えてください''',
            'content': '英語での質問も一部ありました。',
            'title': '一次面接'
        },
        {
            'company': companies[2],
            'date': today - timedelta(days=12),
            'interview_stage': 'グループディスカッション',
            'interview_date': today - timedelta(days=12),
            'interview_questions': '''（グループテーマ）新しいSNS機能を企画してください
自分の意見を述べる際に意識したことは？
他のメンバーの意見にどう対応しましたか？''',
            'content': '5人グループでのディスカッション。積極的に発言できた。',
            'title': 'GD参加メモ'
        },
        {
            'company': companies[3],
            'date': today - timedelta(days=25),
            'interview_stage': '一次面接',
            'interview_date': today - timedelta(days=25),
            'interview_questions': '''メルカリのサービスをどう思いますか？
プログラミングで作った作品について教えてください
困難なバグに遭遇したとき、どう解決しますか？
チームメンバーと意見が対立したらどうしますか？''',
            'content': 'カジュアルな雰囲気。技術的な深掘りが多かった。',
            'title': '一次面接振り返り'
        },
        {
            'company': companies[3],
            'date': today - timedelta(days=18),
            'interview_stage': '二次面接',
            'interview_date': today - timedelta(days=18),
            'interview_questions': '''メルカリでやりたいことは何ですか？
最近のプロジェクトで工夫した点は？
アルゴリズムの知識はどの程度ありますか？
リモートワークについてどう考えていますか？''',
            'content': '技術課題のレビューあり。フィードバックが丁寧でした。',
            'title': '二次面接メモ'
        }
    ]
    
    for memo_data in past_memos_data:
        Memo.objects.using(db_alias).create(
            account=account,
            company=memo_data['company'],
            date=memo_data['date'],
            interview_stage=memo_data['interview_stage'],
            interview_date=memo_data['interview_date'],
            interview_questions=memo_data['interview_questions'],
            content=memo_data['content'],
            title=memo_data['title']
        )
    
    # 未来の予定を作成
    future_memos_data = [
        {
            'company': companies[0],
            'date': today + timedelta(days=3),
            'interview_stage': '最終面接',
            'interview_date': today + timedelta(days=3),
            'content': '最終面接の予定。役員面接とのこと。',
            'title': '最終面接予定'
        },
        {
            'company': companies[1],
            'date': today + timedelta(days=5),
            'interview_stage': '二次面接',
            'interview_date': today + timedelta(days=5),
            'content': '技術面接の予定。コーディングテストあるかも。',
            'title': '二次面接予定'
        },
        {
            'company': companies[2],
            'date': today + timedelta(days=7),
            'interview_stage': '一次面接',
            'interview_date': today + timedelta(days=7),
            'content': 'オンラインでの一次面接。',
            'title': '一次面接予定'
        },
        {
            'company': companies[4],
            'date': today + timedelta(days=10),
            'interview_stage': '説明会',
            'interview_date': today + timedelta(days=10),
            'content': '会社説明会に参加予定。',
            'title': '説明会'
        },
        {
            'company': companies[4],
            'date': today + timedelta(days=2),
            'interview_stage': 'ES提出',
            'interview_date': today + timedelta(days=2),
            'content': 'エントリーシート提出締切',
            'title': 'ES締切'
        }
    ]
    
    for memo_data in future_memos_data:
        Memo.objects.using(db_alias).create(
            account=account,
            company=memo_data['company'],
            date=memo_data['date'],
            interview_stage=memo_data['interview_stage'],
            interview_date=memo_data['interview_date'],
            content=memo_data['content'],
            title=memo_data['title']
        )
    
    # 質問回答データを作成（一部の質問に回答済み）
    question_answers_data = [
        {
            'company': companies[0],
            'question': '志望動機を教えてください',
            'answer': '''御社のメディア事業、特にAbemaTVの成長に魅力を感じています。
学生時代に動画配信プラットフォームの開発経験があり、その知見を活かしながら、
新しいエンターテイメントの形を作り出したいと考えています。
また、挑戦を推奨する企業文化も自分の成長につながると感じました。'''
        },
        {
            'company': companies[0],
            'question': '学生時代に最も力を入れたことは何ですか？',
            'answer': '''大学のプログラミングサークルでWebアプリケーションの開発プロジェクトに取り組みました。
チームリーダーとして5人のメンバーをまとめ、3ヶ月で学内情報共有サービスを完成させました。
技術面では、React/Node.jsを使った開発スキルを習得し、
チームマネジメントではメンバーの強みを活かしたタスク分担を心がけました。'''
        },
        {
            'company': companies[0],
            'question': 'あなたの強みと弱みを教えてください',
            'answer': '''強み：新しい技術を学ぶことが好きで、独学でも積極的に学習できる点です。
最近ではGoやTypeScriptなど、トレンドの技術を習得しました。
弱み：完璧主義な面があり、時に時間をかけすぎてしまうことです。
最近は、MVPを早く作ってフィードバックをもらうことを意識して改善中です。'''
        },
        {
            'company': companies[1],
            'question': 'なぜ楽天を志望しているのですか？',
            'answer': '''楽天経済圏という独自のエコシステムに魅力を感じています。
ECだけでなく、金融、通信、旅行など多様なサービスが連携している点が特徴的で、
そこで横断的な開発経験を積みたいと考えています。
また、グローバル展開にも力を入れており、世界を舞台に働ける環境にも惹かれました。'''
        },
        {
            'company': companies[2],
            'question': 'メルカリのサービスをどう思いますか？',
            'answer': ''
        }
    ]
    
    for qa_data in question_answers_data:
        QuestionAnswer.objects.using(db_alias).create(
            account=account,
            company=qa_data['company'],
            question=qa_data['question'],
            answer=qa_data['answer']
        )


def remove_sample_data(apps, schema_editor):
    Account = apps.get_model('team_UD', 'Account')
    db_alias = schema_editor.connection.alias
    
    # アカウント1のデータを削除（カスケードで関連データも削除される）
    try:
        account = Account.objects.using(db_alias).get(id=1)
        # メモと質問回答を削除
        account.memo_set.all().delete()
        account.questionanswer_set.all().delete()
    except Account.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('team_UD', '0011_questionanswer'),
    ]

    operations = [
        migrations.RunPython(add_sample_data, remove_sample_data),
    ]
