from django.db import migrations


def migrate_books_to_book_table(apps, schema_editor):
    """既存のBookReviewからBookテーブルにデータを移行"""
    BookReview = apps.get_model('graphics', 'BookReview')
    Book = apps.get_model('graphics', 'Book')
    
    db_alias = schema_editor.connection.alias
    
    # ISBNがあるレビューを取得
    reviews_with_isbn = BookReview.objects.using(db_alias).exclude(isbn='').exclude(isbn__isnull=True)
    
    books_created = 0
    reviews_updated = 0
    
    # ISBNごとにグループ化して処理
    processed_isbns = set()
    
    for review in reviews_with_isbn:
        isbn = review.isbn
        
        if isbn in processed_isbns:
            # 既に処理済みのISBN：Bookレコードを取得してリンク
            try:
                book = Book.objects.using(db_alias).get(isbn=isbn)
                review.book = book
                review.save(using=db_alias)
                reviews_updated += 1
            except Book.DoesNotExist:
                pass
        else:
            # 新しいISBN：Bookレコードを作成
            book, created = Book.objects.using(db_alias).get_or_create(
                isbn=isbn,
                defaults={
                    'title': review.title,
                    'author': review.author,
                    'publication_date': review.publication_date,
                    'cover_image_url': review.cover_image_url,
                }
            )
            
            if created:
                books_created += 1
            
            # レビューをBookにリンク
            review.book = book
            review.save(using=db_alias)
            reviews_updated += 1
            processed_isbns.add(isbn)
    
    print(f"マイグレーション完了: {books_created}冊の書籍を作成、{reviews_updated}件のレビューを更新")


def reverse_migration(apps, schema_editor):
    """ロールバック：BookReviewのbookフィールドをクリア"""
    BookReview = apps.get_model('graphics', 'BookReview')
    db_alias = schema_editor.connection.alias
    
    BookReview.objects.using(db_alias).update(book=None)


class Migration(migrations.Migration):

    dependencies = [
        ('graphics', '0015_book_bookreview_book'),
    ]

    operations = [
        migrations.RunPython(migrate_books_to_book_table, reverse_migration),
    ]
