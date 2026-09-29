from src.ingestion.validation import validate_amount


def test_valid_amount():
    assert validate_amount(100) == ""


def test_negative_amount():
    assert validate_amount(-50) == "Amount must be greater than 0"


def test_non_numeric_amount():
    assert validate_amount("ABC") == "Amount must be numeric"