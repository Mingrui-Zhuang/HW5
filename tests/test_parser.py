from datetime import date
import pytest
from nldate.parser import parse

def test_absolute_date():
    assert parse("May 1st, 2026") == date(2026, 5, 1)

def test_relative_days_before():
    assert parse("5 days before May 1st, 2026") == date(2026, 4, 26)

def test_relative_days_after():
    assert parse("3 days after 2026-05-13") == date(2026, 5, 16)

def test_next_tuesday():
    today = date(2026, 5, 11)  # Monday
    assert parse("next Tuesday", today=today) == date(2026, 5, 12)

def test_years_months():
    today = date(2026, 5, 1)
    assert parse("1 year and 2 months after yesterday", 
                 today=today) == date(2027, 6, 30)

def test_last_monday():
    today = date(2026, 5, 13) # Wednesday
    assert parse("last Monday", today=today) == date(2026, 5, 11)

def test_in_x_days():
    today = date(2026, 5, 10)
    assert parse("in 10 days", today=today) == date(2026, 5, 20)

def test_tomorrow():
    today = date(2026, 5, 10)
    assert parse("tomorrow", today=today) == date(2026, 5, 11)

def test_yesterday():
    today = date(2026, 5, 1)
    assert parse("yesterday", today=today) == date(2026, 4, 30)


"""Tests for nldate.parser.parse()"""
import pytest
from datetime import date
from nldate.parser import parse

TODAY = date(2025, 6, 11)   # Wednesday

# ── Absolute dates ──────────────────────────────────────────────────────────
@pytest.mark.parametrize("s,expected", [
    ("Dec 1, 2025",           date(2025, 12, 1)),
    ("December 1, 2025",      date(2025, 12, 1)),
    ("1 Dec 2025",            date(2025, 12, 1)),
    ("1st December 2025",     date(2025, 12, 1)),
    ("2025-12-01",            date(2025, 12, 1)),
    ("12/01/2025",            date(2025, 12, 1)),
    ("Jan 15, 2024",          date(2024, 1, 15)),
    ("15 January 2024",       date(2024, 1, 15)),
    ("March 3, 2020",         date(2020, 3, 3)),
])
def test_absolute_dates(s, expected):
    assert parse(s, today=TODAY) == expected


# ── today / tomorrow / yesterday ────────────────────────────────────────────
def test_today():      assert parse("today",     today=TODAY) == TODAY
def test_tomorrow():   assert parse("tomorrow",  today=TODAY) == date(2025, 6, 12)
def test_yesterday():  assert parse("yesterday", today=TODAY) == date(2025, 6, 10)


# ── Relative weekdays ───────────────────────────────────────────────────────
# TODAY = Wednesday (wd=2)
@pytest.mark.parametrize("s,expected", [
    ("next Monday",     date(2025, 6, 16)),   # +4 days
    ("next Friday",     date(2025, 6, 13)),   # +2 days
    ("next Wednesday",  date(2025, 6, 18)),   # same weekday → +7
    ("last Monday",     date(2025, 6,  9)),   # −2 days
    ("last Friday",     date(2025, 6,  6)),   # −6 days
    ("last Wednesday",  date(2025, 6,  4)),   # same weekday → −7
    ("this Friday",     date(2025, 6, 13)),
    ("this Monday",     date(2025, 6, 16)),   # 'this' when past → next occurrence
])
def test_relative_weekdays(s, expected):
    assert parse(s, today=TODAY) == expected


# ── Simple day/week offsets ──────────────────────────────────────────────────
@pytest.mark.parametrize("s,expected", [
    ("in 3 days",           date(2025, 6, 14)),
    ("3 days from now",     date(2025, 6, 14)),
    ("3 days from today",   date(2025, 6, 14)),
    ("3 days later",        date(2025, 6, 14)),
    ("3 days ago",          date(2025, 6,  8)),
    ("in 2 weeks",          date(2025, 6, 25)),
    ("2 weeks ago",         date(2025, 5, 28)),
    ("in 1 week",           date(2025, 6, 18)),
    ("a week from now",     date(2025, 6, 18)),
    ("10 days ago",         date(2025, 6,  1)),
])
def test_day_week_offsets(s, expected):
    assert parse(s, today=TODAY) == expected


# ── Month / year offsets ─────────────────────────────────────────────────────
@pytest.mark.parametrize("s,expected", [
    ("in 1 month",          date(2025, 7, 11)),
    ("2 months ago",        date(2025, 4, 11)),
    ("in 1 year",           date(2026, 6, 11)),
    ("1 year ago",          date(2024, 6, 11)),
    ("in 6 months",         date(2025, 12, 11)),
    ("3 years from now",    date(2028, 6, 11)),
])
def test_month_year_offsets(s, expected):
    assert parse(s, today=TODAY) == expected


# ── Relative to an explicit anchor ──────────────────────────────────────────
@pytest.mark.parametrize("s,expected", [
    ("3 days after Dec 1, 2025",          date(2025, 12,  4)),
    ("3 days before Dec 1, 2025",         date(2025, 11, 28)),
    ("1 week after Dec 1, 2025",          date(2025, 12,  8)),
    ("2 months before March 3, 2020",     date(2020,  1,  3)),
    ("1 year after Jan 15, 2024",         date(2025,  1, 15)),
    ("5 days after tomorrow",             date(2025, 6, 17)),
    ("1 week before next Monday",         date(2025, 6,  9)),
])
def test_offset_from_anchor(s, expected):
    assert parse(s, today=TODAY) == expected


# ── Combinations (multiple units) ────────────────────────────────────────────
@pytest.mark.parametrize("s,expected", [
    ("2 years and 3 months after today",        date(2027, 9, 11)),
    ("1 year and 2 months from now",            date(2026, 8, 11)),
    ("2 years and 3 months before today",       date(2023, 3, 11)),
    ("1 year and 6 months after Dec 1, 2025",   date(2027, 6,  1)),
    ("3 months and 5 days from now",            date(2025, 9, 16)),
])
def test_combinations(s, expected):
    assert parse(s, today=TODAY) == expected


# ── Written numbers ───────────────────────────────────────────────────────────
@pytest.mark.parametrize("s,expected", [
    ("three days from now",   date(2025, 6, 14)),
    ("two weeks ago",         date(2025, 5, 28)),
    ("a month from now",      date(2025, 7, 11)),
    ("an hour from now",      None),  # unsupported unit → ValueError
])
def test_written_numbers(s, expected):
    if expected is None:
        with pytest.raises(ValueError):
            parse(s, today=TODAY)
    else:
        assert parse(s, today=TODAY) == expected


# ── Error handling ────────────────────────────────────────────────────────────
def test_unparseable_raises():
    with pytest.raises(ValueError):
        parse("sometime next year maybe", today=TODAY)

def test_empty_raises():
    with pytest.raises((ValueError, Exception)):
        parse("", today=TODAY)


# ── Default today (smoke test) ────────────────────────────────────────────────
def test_default_today():
    result = parse("today")
    assert result == date.today()