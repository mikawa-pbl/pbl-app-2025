"""
Utility functions for graphics app
"""

import urllib.request
import json
import re


def format_author_name(author_raw):
    """
    Format author name by removing birth year and replacing commas with spaces

    Args:
        author_raw (str): Raw author name (e.g., "斎藤,康毅,1984-")

    Returns:
        str: Formatted author name (e.g., "斎藤 康毅")
    """
    if not author_raw:
        return None

    # Remove birth year pattern (e.g., "1984-")
    author = re.sub(r',?\s*\d{4}-?\s*', '', author_raw)

    # Replace commas with spaces
    author = author.replace(',', ' ')

    # Remove extra spaces
    author = ' '.join(author.split())

    return author if author else None


def format_publication_date(pubdate_raw):
    """
    Format publication date from YYYYMM to YYYY年MM月

    Args:
        pubdate_raw (str): Raw publication date (e.g., "202404")

    Returns:
        str: Formatted date (e.g., "2024年04月") or None
    """
    if not pubdate_raw:
        return None

    # Expected format: YYYYMM
    if len(pubdate_raw) >= 6 and pubdate_raw[:6].isdigit():
        year = pubdate_raw[:4]
        month = pubdate_raw[4:6]
        return f"{year}年{month}月"

    return None


def fetch_book_info_from_openbd(isbn):
    """
    Fetch book information from OpenBD API

    Args:
        isbn (str): ISBN code

    Returns:
        dict: Book information (title, author, publication_date) or None
    """
    url = f"https://api.openbd.jp/v1/get?isbn={isbn}"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

            if data and data[0]:
                book_data = data[0]

                # Get title
                title = None
                if 'summary' in book_data and 'title' in book_data['summary']:
                    title = book_data['summary']['title']

                # Get author and format it
                author = None
                if 'summary' in book_data and 'author' in book_data['summary']:
                    author_raw = book_data['summary']['author']
                    author = format_author_name(author_raw)

                # Get publication date and format it
                publication_date = None
                if 'summary' in book_data and 'pubdate' in book_data['summary']:
                    pubdate_raw = book_data['summary']['pubdate']
                    publication_date = format_publication_date(pubdate_raw)

                return {
                    'title': title,
                    'author': author,
                    'publication_date': publication_date
                }
            else:
                return None

    except Exception as e:
        # Return None if error occurs
        print(f"OpenBD API Error: {e}")
        return None
