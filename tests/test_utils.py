"""Tests for utils.py"""
import datetime
import pytest
from unittest.mock import patch
from utils import format_date, truncate, confirm


class TestFormatDate:
    def test_returns_string(self):
        result = format_date(datetime.datetime(2024, 1, 15, 9, 5))
        assert isinstance(result, str)

    def test_known_datetime(self):
        dt = datetime.datetime(2024, 6, 1, 13, 30)
        assert format_date(dt) == "2024-06-01 13:30"

    def test_midnight(self):
        dt = datetime.datetime(2023, 12, 31, 0, 0)
        assert format_date(dt) == "2023-12-31 00:00"

    def test_end_of_day(self):
        dt = datetime.datetime(2023, 1, 1, 23, 59)
        assert format_date(dt) == "2023-01-01 23:59"

    def test_none_uses_now(self):
        fixed = datetime.datetime(2024, 3, 15, 10, 45)
        with patch("utils.datetime.datetime") as mock_dt:
            mock_dt.now.return_value = fixed
            mock_dt.strftime = datetime.datetime.strftime
            # Call real format_date with None — it calls datetime.datetime.now()
            result = format_date(None)
        assert result == "2024-03-15 10:45"

    def test_default_arg_is_none(self):
        # Verify the default argument behavior — calling with no args should not raise
        with patch("utils.datetime") as mock_dt_module:
            fixed = datetime.datetime(2024, 5, 20, 8, 0)
            mock_dt_module.datetime.now.return_value = fixed
            mock_dt_module.datetime.strftime = datetime.datetime.strftime
            result = format_date()
        assert result == "2024-05-20 08:00"

    def test_single_digit_month_and_day_padded(self):
        dt = datetime.datetime(2024, 1, 5, 3, 7)
        assert format_date(dt) == "2024-01-05 03:07"


class TestTruncate:
    def test_short_text_unchanged(self):
        assert truncate("hello") == "hello"

    def test_exactly_max_len_unchanged(self):
        text = "a" * 50
        assert truncate(text) == text

    def test_over_max_len_truncated(self):
        text = "a" * 51
        result = truncate(text)
        assert result == "a" * 47 + "..."

    def test_truncated_length_is_max_len(self):
        text = "x" * 100
        result = truncate(text)
        assert len(result) == 50

    def test_ends_with_ellipsis(self):
        text = "hello world this is a long description that goes on and on"
        result = truncate(text)
        assert result.endswith("...")

    def test_custom_max_len(self):
        text = "hello world"
        assert truncate(text, max_len=5) == "he..."

    def test_custom_max_len_exact_fit(self):
        assert truncate("hello", max_len=5) == "hello"

    def test_custom_max_len_one_over(self):
        result = truncate("helloo", max_len=5)
        assert result == "he..."
        assert len(result) == 5

    def test_empty_string(self):
        assert truncate("") == ""

    def test_single_char(self):
        assert truncate("a") == "a"

    def test_unicode_text(self):
        text = "こんにちは世界" * 10
        result = truncate(text)
        assert len(result) == 50
        assert result.endswith("...")

    def test_max_len_three(self):
        result = truncate("abcdef", max_len=3)
        assert result == "..."
        assert len(result) == 3

    def test_preserves_exact_content_before_ellipsis(self):
        text = "abcdefghij" * 6  # 60 chars
        result = truncate(text, max_len=10)
        assert result == "abcdefg..."


class TestConfirm:
    @pytest.mark.parametrize("user_input,expected", [
        ("y", True),
        ("Y", True),
        ("yes", True),
        ("YES", True),
        ("Yes", True),
        ("n", False),
        ("N", False),
        ("no", False),
        ("nope", False),
        ("", False),
        ("maybe", False),
        ("  ", False),
    ])
    def test_responses(self, user_input, expected):
        with patch("builtins.input", return_value=user_input):
            assert confirm("Continue?") == expected

    def test_prompt_passed_to_input(self):
        with patch("builtins.input", return_value="n") as mock_input:
            confirm("Are you sure?")
            mock_input.assert_called_once_with("Are you sure? (y/n): ")

    def test_returns_bool(self):
        with patch("builtins.input", return_value="y"):
            result = confirm("Proceed?")
            assert isinstance(result, bool)

    def test_non_string_prompt_raises(self):
        with pytest.raises(ValueError):
            confirm(None)

    def test_empty_prompt_raises(self):
        with pytest.raises(ValueError):
            confirm("")

    def test_eoferror_returns_false(self):
        with patch("builtins.input", side_effect=EOFError):
            assert confirm("Proceed?") is False

    def test_strip_whitespace_response(self):
        with patch("builtins.input", return_value="  y  "):
            assert confirm("Go?") is True


class TestFormatDateTypeCheck:
    def test_non_datetime_raises_typeerror(self):
        with pytest.raises(TypeError):
            format_date("2024-01-01")

    def test_integer_raises_typeerror(self):
        with pytest.raises(TypeError):
            format_date(12345)


class TestTruncateTypeCheck:
    def test_non_string_raises_typeerror(self):
        with pytest.raises(TypeError):
            truncate(123)

    def test_zero_max_len_raises(self):
        with pytest.raises(ValueError):
            truncate("hello", max_len=0)

    def test_negative_max_len_raises(self):
        with pytest.raises(ValueError):
            truncate("hello", max_len=-1)

    def test_float_max_len_raises(self):
        with pytest.raises(ValueError):
            truncate("hello", max_len=1.5)
