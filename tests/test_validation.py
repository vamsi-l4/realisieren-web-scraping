from processing.validation import validate_record


def valid_record():
    return {
        "source": "Books to Scrape", "source_url": "https://books.toscrape.com/book.html",
        "name_or_title": "Example", "price": 12.5, "rating": 3,
    }


def test_valid_record_has_no_reasons():
    assert validate_record(valid_record()) == []


def test_invalid_fields_return_useful_reasons():
    record = valid_record()
    record.update(source="unknown", source_url="ftp://bad", name_or_title="", price=-1, rating=6)
    assert validate_record(record) == [
        "unknown_source", "missing_name_or_title", "invalid_source_url", "invalid_price", "invalid_rating"
    ]
