# アプリ設計メモ

## データベース設計
論文題目
論文著者
会議名／雑誌名
年度
DOI
URL（IEEE xplore/ACM DL）


uv run python manage.py dbshell --database=teachers

<SQLite Command>
INSERT INTO teachers_paper(title, author, year, booktitle, url, doi) VALUES ("高度専門人材育成訓練演習の作り方", "Ohmura Ren", "2025", "TUT紀要", "http://usl.cs.tut.ac.jp", "doi://11.22.33.44");
INSERT INTO teachers_paper(title, author, year, booktitle, url, doi) VALUES ("言語処理", "Akiba Tomoyoshi", "2022", "Computational Linguistics", "http://nlp.cs.tut.ac.jp", "doi://22.33.44.55");
INSERT INTO teachers_paper(title, author, year, booktitle, url, doi) VALUES ("運動制御", "Fukumura Naohiro", "2023", "Motor Control", "http://bmcs.cs.tut.ac.jp", "doi://33.44.55.66");