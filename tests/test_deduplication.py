from processing.deduplication import find_duplicates


def test_book_duplicates_ignore_case_whitespace_and_punctuation():
    records = [
        {"source": "Books to Scrape", "name_or_title": "Example, Book!"},
        {"source": "Books to Scrape", "name_or_title": " example book "},
        {"source": "Books to Scrape", "name_or_title": "DIFFERENT BOOK"},
    ]
    unique, duplicates = find_duplicates(records)
    assert len(unique) == 2
    assert len(duplicates) == 1


def test_quote_duplicates_use_author_and_first_fifty_characters():
    base = "A long sample quote that is the same throughout the first fifty characters"
    records = [
        {"source": "Quotes to Scrape", "author": "Jane Doe", "name_or_title": base + " ending"},
        {"source": "Quotes to Scrape", "author": "JANE DOE", "name_or_title": base[:50] + " different"},
        {"source": "Quotes to Scrape", "author": "Other", "name_or_title": base},
    ]
    unique, duplicates = find_duplicates(records)
    assert len(unique) == 2
    assert len(duplicates) == 1
