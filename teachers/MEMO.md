# アプリ設計メモ

## データベース設計
*論文題目
*論文著者
*会議名／雑誌名
*年度
*DOI
*URL （IEEE xplore/ACM DL）


### データベースを更新したとき
(PBLプロジェクトのトップで)
uv run python manage.py makemigration --database=teachers
uv run python manage.py migrate --database=teachers

### データベースへの接続（確認)
uv run python manage.py dbshell --database=teachers

### サーバーの稼働
uv run python manage.py runserver

## SQLite Command
INSERT INTO teachers_paper(title, author, year, booktitle, url, doi) VALUES ("高度専門人材育成訓練演習の作り方", "Ohmura Ren", "2025", "TUT紀要", "http://usl.cs.tut.ac.jp", "doi://11.22.33.44");
INSERT INTO teachers_paper(title, author, year, booktitle, url, doi) VALUES ("言語処理", "Akiba Tomoyoshi", "2022", "Computational Linguistics", "http://nlp.cs.tut.ac.jp", "doi://22.33.44.55");
INSERT INTO teachers_paper(title, author, year, booktitle, url, doi) VALUES ("運動制御", "Fukumura Naohiro", "2023", "Motor Control", "http://bmcs.cs.tut.ac.jp", "doi://33.44.55.66");

## 今後やろうと思うこと
DBの設計(追加項目)
 - 通し番号(ID)
 - *登録者（できれば自動）
 - *登録時刻（自動）
 - （論文PDF）
 - （あれば輪講スライド）
 - （あれば，代表的な画像）
  -- キーワード
  -- *論文概要
  -- *先行研究との比較
  -- *技術や手法の中心的アイデア
  -- *有効性の検証方法
  -- *議論（利点，欠点，制限）
  -- 自身の研究との関連性
  -- その他
 - 修正履歴を残すようにする

機能設計
　現状：一覧，個別情報，登録，検索
  -- 修正（削除含む）
  -- （bibtex生成機能）
  -- bibtexから読み込み(？)
　

## データベース
*通し番号:ID
*論文題目:title
*論文著者:author
*掲載誌名:booktitle
*年:year
*DOI:DOI
*URL:URL
*登録者:submitter
*登録時刻:submit_time 
キーワード:keywords
*どんな論文か:imp_overview
*先行研究との比較:imp_comparison
*技術や手法の中心的アイデア:imp_idea
*有効性の検証方法と結果:imp_usefulness
*議論（利点，欠点，制限）:imp_discussion
自身の研究との関連性:imp_relation
その他:note
論文PDF:paper_file
輪講スライド:rc_slide
代表的な画像:paper_figure

## 一覧に表示する項目
*IDはいらない
*論文題目
*論文著者
*年
*論文誌
*登録者
*登録時刻

## 追加機能
* ソートの順を切り替える機能