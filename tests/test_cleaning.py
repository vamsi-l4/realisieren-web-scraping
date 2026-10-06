from processing.cleaning import clean_price, clean_quote_marks, clean_rating, clean_tags, clean_text, normalize_url


def test_text_and_quote_mark_cleaning():
    assert clean_text("  Hello \n World ") == "Hello World"
    assert clean_quote_marks("“  Hello \n World ”") == "Hello World"


def test_numeric_and_tag_cleaning():
    assert clean_price("£51.77") == 51.77
    assert clean_rating("star-rating Three") == 3
    assert clean_tags([" Life ", "love", "LIFE"]) == "life;love"


def test_url_normalization():
    assert normalize_url("../book", "https://example.com/list/page.html") == "https://example.com/book"
    assert normalize_url("javascript:alert(1)") is None
